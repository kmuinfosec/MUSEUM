from museum.core import preprocess
from museum.data.elasticsearch.template import get_index_template, get_bulk_data, get_search_body, get_multisearch_data
from museum.exception import *
from museum.common.utils import *
from museum.common.report import make_report_hits

from elasticsearch import Elasticsearch, ConnectionTimeout
import os


class MUSEUM:
    def __init__(self, host, port, use_caching=False):
        self.es = Elasticsearch(hosts=host, port=port, timeout=600)
        self.use_caching = use_caching

    def create_index(self, index, module, num_hash=128, use_smallest=False,
                     use_mod=False, use_minmax=False, shards=5, replicas=1):
        if index == '':
            raise BaseException("Index parameter is empty")
        if self.es.indices.exists(index):
            raise AlreadyExistError("{} is already exist index".format(index))

        res = self.es.indices.create(
            index=index,
            body=get_index_template(module, num_hash, use_smallest, use_mod, use_minmax, shards, replicas)
        )
        return res

    def get_index_metadata(self, index_name):
        if not self.es.indices.exists(index_name):
            raise NotExistError("Index doesn't exist")
        index_info = self.es.indices.get_mapping(index=index_name)[index_name]['mappings']['_meta']
        return index_info

    def bulk_index(self, index_name, target, process_count=8, batch_size=10000):
        index_info = self.get_index_metadata(index_name)

        if type(target) is list or type(target) is set:
            file_list = target
        elif type(target) is str and os.path.isdir(target):
            file_list = walk_directory(target)
        else:
            raise NotADirectoryError("{} is not a directory".format(target))

        for jobs in batch_generator(file_list, batch_size):
            bulk_data_list = []
            for file_md5, samples, feature_size, file_name in mp_helper(preprocess.do, jobs, process_count,
                                                                        index_info=index_info,
                                                                        use_caching=self.use_caching,
                                                                        desc="bulk preprocess"):
                if samples:
                    bulk_data_list.append(get_bulk_data(file_md5, samples, feature_size, file_name, index_info))

            self.es.bulk(body=bulk_data_list)

    def search(self, index_name, file_path, limit=1, index_info=None):
        if not index_info:
            index_info = self.get_index_metadata(index_name)
        _, query_samples, query_feature_size, file_name = preprocess.do(file_path, index_info, self.use_caching)

        report = {'query': file_name, 'hits': []}
        if query_samples:
            try:
                response = self.es.search(index=index_name, body=get_search_body(query_samples, limit), search_type='dfs_query_then_fetch')
            except ConnectionTimeout:
                print('Search error detected')
                return report
            report['hits'] = make_report_hits(response, query_samples, query_feature_size, index_info)
        return report

    def multi_search(self, index_name, target, limit=1, process_count=1, batch_size=100):
        if type(target) is list or type(target) is set:
            file_list = target
        elif type(target) is str and os.path.isdir(target):
            file_list = walk_directory(target)
        else:
            raise NotADirectoryError("{} is not a directory".format(target))
        index_info = self.get_index_metadata(index_name)
        for jobs in batch_generator(file_list, batch_size):
            search_data_list = []
            query_samples_list = []
            query_feature_size_list = []
            file_name_list = []
            for _, query_samples, query_feature_size, file_name in mp_helper(preprocess.do, jobs, process_count,
                                                                             index_info=index_info,
                                                                             use_caching=self.use_caching,
                                                                             tqdm_disable=True):
                if query_samples:
                    search_data_list.append(get_multisearch_data(index_name, query_samples, limit))
                    query_samples_list.append(query_samples)
                    query_feature_size_list.append(query_feature_size)
                    file_name_list.append(file_name)
            try:
                resp = self.es.msearch(body="\n".join(search_data_list))
            except ConnectionTimeout:
                print('Search error detected')
                continue
            report_list = []
            for i, response in enumerate(resp['responses']):
                report = {'query': file_name_list[i],
                          'hits': make_report_hits(response, query_samples_list[i],
                                                   query_feature_size_list[i], index_info)}
                report_list.append(report)

            yield report_list
