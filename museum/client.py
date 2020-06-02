from museum.core.similarity import get_similarity
from museum.core.process import preprocess
from museum.core.data import create_mapping_form, create_query, create_document
from museum.exception import *
from museum.util import *

from elasticsearch import Elasticsearch, helpers, ConnectionTimeout
from tqdm import tqdm
import os
import json

class Museum:
    def __init__(self, host, port):
        self.es = Elasticsearch(hosts=host, port=port, timeout=600)

    def create_index(self, index, module, hash_count=128, use_smallest=False,
                     use_mod=False, use_minmax=False, shards=5, replicas=1):
        if index == '':
            raise BaseException("Index parameter is empty")
        if self.es.indices.exists(index):
            raise AlreadyExistError("Already exist index name")

        mapping_json = json.dumps(create_mapping_form(module, hash_count, use_smallest,
                                  use_mod, use_minmax, shards, replicas))

        res = self.es.indices.create(index=index, body=mapping_json, include_type_name=True)
        return res

    def get_index_info(self, index_name):
        if not self.es.indices.exists(index_name):
            raise NotExistError("Index doesn't exist")
        index_info = self.es.indices.get_mapping(index=index_name)[index_name]['mappings']['_meta']
        index_info['index_name'] = index_name
        return index_info

    def insert_bulk(self, index_name, target_dir, process_count=8, batch_size=None, use_caching=True):
        index_info = self.get_index_info(index_name)

        if not os.path.isdir(target_dir):
            raise FileNotFoundError("Target directory doesn't exist")

        file_list = walk_directory(target_dir)
        batch_list = get_batch_list(file_list, batch_size)
        for batch in batch_list:
            doc_list = []
            for preprocess_items in multiprocessing_helper(preprocess, batch, process_count,
                                                           index_info=index_info, use_caching=use_caching):
                document = create_document(preprocess_items, index_info['index_name'])
                if document:
                    doc_list.append(document)

            for ok, response in tqdm(helpers.parallel_bulk(self.es, doc_list, thread_count=process_count),
                                     total=len(doc_list), desc='indexing'):
                if not ok:
                    print(response)

    def search(self, index_name, file_path, limit=1, use_caching=False):
        index_info = self.get_index_info(index_name)
        preprocess_items = preprocess(file_path, index_info, use_caching)
        query = create_query(preprocess_items, limit)
        if query:
            try:
                response = self.es.search(index=index_name, body=json.dumps(query), search_type='dfs_query_then_fetch')
            except ConnectionTimeout:
                print('Search error detected')
                return
            similar_list = get_similarity(preprocess_items[0], response, preprocess_items[1], index_info)
            report = {'query': preprocess_items[2], 'hits': similar_list}
            return report
        else:
            report = {'query': preprocess_items[2], 'hits': []}
            return report

    def search_bulk(self, index_name, target_dir, limit=1, process_count=1, batch_size=None, use_caching=False,
                    tqdm_disable=False):
        index_info = self.get_index_info(index_name)
        if not os.path.isdir(target_dir):
            raise BaseException("Target directory doesn't exist")

        file_list = walk_directory(target_dir)

        batch_list = get_batch_list(file_list, batch_size)
        for batch in tqdm(batch_list, disable=tqdm_disable):
            for preprocess_items in multiprocessing_helper(preprocess, batch, process_count, index_info=index_info,
                                                           use_caching=use_caching, tqdm_disable=True):
                query = create_query(preprocess_items, limit)
                if preprocess_items:
                    try:
                        response = self.es.search(index=index_name, body=json.dumps(query),
                                                  search_type='dfs_query_then_fetch')
                    except ConnectionTimeout:
                        print('Search error detected')
                        return
                    similar_list = get_similarity(preprocess_items[0], response, preprocess_items[1], index_info)
                    report = {'query': preprocess_items[2], 'hits': similar_list}
                else:
                    report = {'query': preprocess_items[2], 'hits': []}
                yield report

