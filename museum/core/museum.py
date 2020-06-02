from museum.core.similarity import get_similarity
from museum.core.process import preprocess
from museum.core.data import get_mapping_form, get_document_dict, create_query
from museum.exception import *
from museum.util import *

from elasticsearch import Elasticsearch, helpers, ConnectionTimeout
from tqdm import tqdm
import os
import json
import sys

class Museum:

    def __init__(self, host, port):
        self.es = Elasticsearch(hosts=host, port=port, timeout=600)
        self.host, self.port = host, port
        self.index = None
        self.module_name = None
        self.module_kwargs = None
        self.hash_count = None
        self.use_k_smallest = None
        self.use_mod = None
        self.use_minmax = None

    def _select_index(self, index):
        if not self.es.indices.exists(index):
            raise NotExistError("Index doesn't exist")
        _meta = self.es.indices.get_mapping(index=index)[index]['mappings']['_meta']
        self.index = index
        self.module_name = _meta['module']
        self.hash_count = _meta['hash_count']
        self.use_k_smallest = _meta['k-smallest']
        self.use_mod = _meta['use_mod']
        if 'use_minmax' not in _meta:
            self.use_minmax = False
        else:
            self.use_minmax = _meta['use_minmax']
        self.module_kwargs = _meta['module_kwargs']

    def create_index(self, index, use_k_smallest=True, hash_count=128, module_name='ae',
                     use_mod=0, use_minmax=False, shards=5, replicas=1, module_kwargs=None):
        if index == '':
            raise BaseException("Index parameter is empty")
        if self.es.indices.exists(index):
            raise AlreadyExistError("Already exist index name")
        if module_name is not None:
            module_check(module_name)

        mapping = get_mapping_form(shards, replicas, use_k_smallest, hash_count, module_name,
                                   use_mod, use_minmax, module_kwargs)
        mapping_json = json.dumps(mapping)

        res = self.es.indices.create(index=index, body=mapping_json, include_type_name=True)
        return res

    def create_document(self, file_path, use_caching=False):
        min_hashes, feature_size, name = self._preprocess(file_path, use_caching)
        if min_hashes is not None:
            return get_document_dict(name, self.index, min_hashes, feature_size)

    def search(self, file_path, index_name=None, limit=1, use_caching=False):
        if index_name is None:
            raise NotDefinedError("Index doesn't selected")
        self._select_index(index_name)

        min_hashes, feature_size, name = self._preprocess(file_path, use_caching)
        if min_hashes is not None:
            json_query = json.dumps(create_query(min_hashes, limit))
            try:
                response = self.es.search(index=index_name, body=json_query, search_type='dfs_query_then_fetch')
            except ConnectionTimeout:
                print('Search error detected')
                return
            similar_list = get_similarity(self.hash_count, min_hashes, response, feature_size,
                                          self.use_k_smallest, self.use_minmax)
            report = {'query': name, 'hits': similar_list}
            return report
        else:
            report = {'query': name, 'hits': []}
            return report

    def insert_bulk(self, index_name, target_dir, process_count=1, batch_size=None, use_caching=True):
        self._select_index(index_name)

        if not os.path.isdir(target_dir):
            raise FileNotFoundError("Target directory doesn't exist")

        file_list = walk_directory(target_dir)
        batch_list = get_batch_list(file_list, batch_size)
        for batch in batch_list:
            doc_list = []
            for doc in self._multiprocessing(self.create_document, batch, process_count, use_caching=use_caching):
                if doc:
                    doc_list.append(doc)

            for ok, response in tqdm(helpers.parallel_bulk(self.es, doc_list, thread_count=process_count),
                                     total=len(doc_list), desc='indexing'):
                if not ok:
                    print(response)

    def search_bulk(self, index_name, target_dir, limit=1, process_count=1, batch_size=None, use_caching=False,
                    tqdm_disable=False):
        if not os.path.isdir(target_dir):
            raise BaseException("Target directory doesn't exist")

        file_list = walk_directory(target_dir)

        batch_list = get_batch_list(file_list, batch_size)
        for batch in batch_list:
            for report in self._multiprocessing(self.search, batch, process_count, index_name=index_name,
                                                limit=limit, use_caching=use_caching, tqdm_disable=tqdm_disable):
                yield report

    def _multiprocessing(self, worker, jobs, process_count=8, tqdm_disable=False, **kwargs):
        with Pool(processes=process_count) as pool:
            for ret in tqdm(pool.imap(partial(self._parallel_call, **kwargs), self._prepare_call(worker.__name__, jobs)),
                            total=len(jobs), desc=worker.__name__, disable=tqdm_disable):
                yield ret

    def _preprocess(self, file_path, use_caching=False):
        if not self.index:
            raise NotDefinedError("Index doesn't selected")
        name = os.path.splitext(os.path.split(file_path)[1])[0]

        is_cached, target_file = check_cached(file_path, self.use_k_smallest, self.hash_count, self.module_name,
                                              self.use_minmax)
        if is_cached:
            min_hashes, feature_size = load_cached_data(target_file)
        else:
            min_hashes, feature_size = preprocess(
                file_path, self.use_k_smallest, self.hash_count, self.module_name, self.use_mod, self.use_minmax,
                self.module_kwargs)
            if use_caching:
                caching(min_hashes, feature_size, target_file,
                        self.use_k_smallest, self.hash_count, self.module_name, self.use_minmax)
        return min_hashes, feature_size, name

    @staticmethod
    def _parallel_call(params, **kwargs):  # a helper for calling 'remote' instances
        cls = getattr(sys.modules[__name__], params[0])  # get our class type
        instance = cls.__new__(cls)  # create a new instance without invoking __init__
        instance.__dict__ = params[1]  # apply the passed state to the new instance
        setattr(instance, 'es', Elasticsearch(hosts=params[1]['host'], port=params[1]['port'], timeout=600))
        method = getattr(instance, params[2])  # get the requested method
        args = params[3] if isinstance(params[3], (list, tuple)) else [params[3]]
        return method(*args, **kwargs)  # expand arguments, call our method and return the result

    def _prepare_call(self, name, args):
        for arg in args:
            instance_property = self.__dict__.copy()
            del instance_property['es']
            yield [self.__class__.__name__, instance_property, name, arg]
