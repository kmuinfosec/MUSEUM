from museum.core import preprocess
from museum.core.similarity import get_similarity
from museum.core.data import get_document_dict, get_query_dict, get_mapping_dict
from museum.exception import *
from museum.utils import *

from elasticsearch import Elasticsearch, helpers, ConnectionTimeout
from tqdm import tqdm
import os
import json


class MUSEUM:
    def __init__(self, host, port, use_caching=True):
        self.es = Elasticsearch(hosts=host, port=port, timeout=600)
        self.use_caching = use_caching

    def create_index(self, index, module, num_hash=128, use_smallest=False,
                     use_mod=False, use_minmax=False, shards=5, replicas=1):
        if index == '':
            raise BaseException("Index parameter is empty")
        if self.es.indices.exists(index):
            raise AlreadyExistError("{} is already exist index".format(index))

        mapping_json = json.dumps(get_mapping_dict(module, num_hash, use_smallest,
                                  use_mod, use_minmax, shards, replicas))

        res = self.es.indices.create(index=index, body=mapping_json)
        return res

    def get_index_info(self, index_name):
        if not self.es.indices.exists(index_name):
            raise NotExistError("Index doesn't exist")
        index_info = self.es.indices.get_mapping(index=index_name)[index_name]['mappings']['_meta']
        return index_info

    def bulk_index(self, index_name, target, process_count=8, batch_size=10000):
        index_info = self.get_index_info(index_name)

        if type(target) is list or type(target) is set:
            file_list = target
        elif type(target) is str and os.path.isdir(target):
            file_list = walk_directory(target)
        else:
            raise NotADirectoryError("{} is not a directory".format(target))

        for jobs in batch_generator(file_list, batch_size):
            docs = []
            for preprocess_items in multiprocessing_helper(
                    preprocess.do, jobs, process_count, index_info=index_info, use_caching=self.use_caching):
                if preprocess_items[1]:
                    docs.append(get_document_dict(preprocess_items, index_name))

            for ok, response in tqdm(helpers.parallel_bulk(self.es, docs, thread_count=process_count),
                                     total=len(docs), desc='indexing'):
                if not ok:
                    print(response)

    def search(self, index_name, file_path, limit=1):
        index_info = self.get_index_info(index_name)
        preprocess_items = preprocess.do(file_path, index_info, self.use_caching)
        query = get_query_dict(preprocess_items[1], limit)
        if query:
            try:
                response = self.es.search(index=index_name, body=json.dumps(query), search_type='dfs_query_then_fetch')
            except ConnectionTimeout:
                print('Search error detected')
                return
            similar_list = get_similarity(response, preprocess_items[1], preprocess_items[2], index_info)
            report = {'query': preprocess_items[3], 'hits': similar_list}
            return report
        else:
            report = {'query': preprocess_items[3], 'hits': []}
            return report

    def bulk_search(self, index_name, target, limit=1, process_count=1, batch_size=None):
        if type(target) is list or type(target) is set:
            file_list = target
        elif type(target) is str and os.path.isdir(target):
            file_list = walk_directory(target)
        else:
            raise NotADirectoryError("{} is not a directory".format(target))
        index_info = self.get_index_info(index_name)
        for jobs in batch_generator(file_list, batch_size):
            for preprocess_items in multiprocessing_helper(
                    preprocess.do, jobs, process_count,
                    index_info=index_info, use_caching=self.use_caching, tqdm_disable=True):
                if preprocess_items[1]:
                    query = get_query_dict(preprocess_items[1], limit)
                    try:
                        response = self.es.search(index=index_name, body=json.dumps(query),
                                                  search_type='dfs_query_then_fetch')
                    except ConnectionTimeout:
                        print('Search error detected')
                        return
                    similar_list = get_similarity(response, preprocess_items[1], preprocess_items[2], index_info)
                    report = {'query': preprocess_items[3], 'hits': similar_list}
                else:
                    report = {'query': preprocess_items[3], 'hits': []}
                yield report
