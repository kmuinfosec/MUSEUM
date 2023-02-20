from museum import template
from museum.functions import preprocess, get_hits_info
from museum.utils import mp, batch_generator, get_file_md5, walk_directory

from elasticsearch import Elasticsearch, ConnectionTimeout
from tqdm import tqdm
from pathlib import Path
import sys


def create_index(host: str, index_name: str, module_name: str, module_params: dict = None, num_hash=128,
                 use_smallest=False, use_minmax=False, use_mod=False, interval=5, shards=5, replicas=1):
    index_name = index_name.strip()
    if index_name == '':
        raise Exception("Invalid index name")

    es = Elasticsearch(host)
    if es.indices.exists(index=index_name):
        raise Exception(f"Index \"{index_name}\" already exists")

    res = es.indices.create(
        index=index_name,
        settings=template.get_settings(interval, shards, replicas),
        mappings=template.get_mappings(module_name, module_params, num_hash, use_smallest, use_minmax, use_mod)
    )
    return res


def delete_index(host: str, index_name: str):
    es = Elasticsearch(host)
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)


def get_index_info(host: str, index_name: str) -> dict:
    es = Elasticsearch(host)
    if not es.indices.exists(index=index_name):
        raise Exception(f"Index \"{index_name}\" does not exist")
    index_info = es.indices.get_mapping(index=index_name)[index_name]['mappings']['_meta']
    index_info['index_name'] = index_name
    return index_info


def bulk(host: str, index_name: str, dir_path: Path, process=8, batch_size=10000, disable_tqdm=False):
    es = Elasticsearch(host, timeout=600)
    index_info = get_index_info(host, index_name)
    path_list = walk_directory(dir_path)
    pbar = tqdm(total=len(path_list), desc="Bulk", file=sys.stdout, disable=disable_tqdm)
    for batch in batch_generator(path_list, batch_size):
        requests = []
        for md5, samples, num_chunks, file_name in mp(preprocess, batch, process, index_info=index_info):
            if samples:
                requests.append(template.get_bulk_request(md5, samples, num_chunks, file_name, index_name))
            pbar.update(1)
        if requests:
            es.bulk(operations=requests)
    pbar.close()


def search(host: str, index_name: str, file_path: Path, limit=1) -> dict:
    es = Elasticsearch(host)
    index_info = get_index_info(host, index_name)
    _, samples, num_chunks, file_name = preprocess(file_path, index_info)
    report = {'query': file_name, 'hits': []}
    if samples:
        try:
            response = es.search(index=index_name, query=template.get_search_query(samples), explain=True, source=True,
                                 size=limit, search_type='dfs_query_then_fetch')
        except ConnectionTimeout:
            print('Connection timeout')
            return report
        report['hits'] = get_hits_info(response, samples, num_chunks, index_info)
    return report


def msearch(host: str, index_name: str, dir_path: Path, limit=1, process=1, batch_size=100, disable_tqdm=False):
    es = Elasticsearch(host, timeout=600)
    index_info = get_index_info(host, index_name)
    path_list = walk_directory(dir_path)
    pbar = tqdm(total=len(path_list), desc="msearch", file=sys.stdout, disable=disable_tqdm)
    for batch in batch_generator(path_list, batch_size):
        requests = []
        samples_list, num_chunks_list, file_name_list = [], [], []
        for _, samples, num_chunks, file_name in mp(preprocess, batch, process, index_info=index_info):
            if samples:
                requests.append(template.get_msearch_request(index_name, samples, limit))
                samples_list.append(samples)
                num_chunks_list.append(num_chunks)
                file_name_list.append(file_name)
            pbar.update(1)

        report_list = []
        if requests:
            try:
                res = es.msearch(searches=requests)
            except ConnectionTimeout:
                print('Search error detected')
                continue
            for i, response in enumerate(res['responses']):
                report = {
                    'query': file_name_list[i],
                    'hits': get_hits_info(response, samples_list[i], num_chunks_list[i], index_info)
                }
                report_list.append(report)
        yield report_list
    pbar.close()


def check_exist(host: str, index_name: str, file_path: Path) -> bool:
    es = Elasticsearch(host)
    status = es.exists(index=index_name, id=get_file_md5(file_path), source=False).meta.status
    return True if status == 200 else False
