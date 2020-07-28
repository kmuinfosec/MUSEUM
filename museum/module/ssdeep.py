from elasticsearch import Elasticsearch, helpers

from musem.algorithm.textmining import calc_idf
from musem.data.loader import load_word_set
from musem.conf import settings
from musem.core.similarity import SimilarityTool
from musem.helper import modulehelper
from musem.exception import *
from multiprocessing import Pool, freeze_support
import os, json, functools, ssdeep

from musem.parser import responseparser


class Musem:

    def __init__(self, **kwargs):
        self.setup_es(**kwargs)
        self.index = None
        self.doc_type = '_doc'
        self.module_name = None

    def setup_es(self, **kwargs):
        host = settings.HOST
        if 'host' in kwargs:
            host = kwargs['host']
        port = settings.PORT
        if 'port' in kwargs:
            port = kwargs['port']
        self.es = Elasticsearch(hosts=host, port=port, timeout=600)

    def set_index(self, index):
        if not self.es.indices.exists(index):
            raise NotExistError("Index doesn't exist")
        self.index = index

    def set_module_name(self, module_name):
        self.module_name = module_name

    def get_module_list(self):
        return modulehelper.get_module_list()

    def create_index(self, index, module_name):
        if index == '':
            raise BaseException("index is blank")
        mapping_json = modulehelper.mapping_loader(module_name)
        request_body = json.dumps(mapping_json)

        if self.es.indices.exists(index):
            raise AlreadyExistError("Index aleady exist")
        res = self.es.indices.create(index=index, body=request_body)
        return res

    @classmethod
    def create_document(cls, file_path, module_name, index, doc_type):
        word_tuple = load_word_set(file_path, module_name)
        return {
            "_index": index,
            "_type": doc_type,
            "_id": os.path.splitext(os.path.split(file_path)[1])[0].split('_')[0],
            "_source": {
                "chunk_size": word_tuple[0],
                "chunk": word_tuple[1],
                "double_chunk": word_tuple[2]
            }
        }

    def insert_bulk(self, target_dir=None):
        if not self.index:
            raise NotDefinedError('set index before this action')
        if not target_dir:
            target_dir = settings.BULK_TARGET_DIR
        if not target_dir or target_dir == '':
            raise BaseException("Bulk directory does not defined")
        elif not os.path.isdir(target_dir):
            raise BaseException("Bulk directory does not exist")

        file_list = list()
        for root, dirs, files in os.walk(target_dir):
            for file_name in files:
                file_list.append(os.path.join(root,file_name))

        division_count = int(len(file_list)/10000)+1
        for i in range(division_count):
            print("Let's insert section of bulk")
            section_list = file_list[i*10000:(i+1)*10000]
            create_document_partial = functools.partial(
                self.create_document,
                module_name=self.module_name, index=self.index, doc_type=self.doc_type
            )
            freeze_support()
            with Pool(processes=settings.PROCESS_NUMBER) as pool:
                action_list = pool.map(create_document_partial, section_list)

            for ok, response in helpers.parallel_bulk(self.es, action_list):
                if not ok:
                    print(response)
            yield int((i+1)/division_count*100)
        return True

    def search_similar_file(self, file_path, limit=1):
        if not self.index:
            raise NotDefinedError('set index before this action')
        word_tuple = load_word_set(file_path, self.module_name)
        file_name = os.path.splitext(os.path.split(file_path)[1])[0]

        st = SimilarityTool(file_name, word_tuple)
        try:
            similar_result = st.exec_search(self.es, self.index, self.doc_type, limit)
        except:
            print('Failed to search. File name : {}'.format(file_name))
            return
        report = st.get_report(similar_result)
        return report

    def search_by_dir(self, search_dir, limit=1, thread_count=settings.PROCESS_NUMBER):

        if not os.path.isdir(search_dir):
            raise BaseException("Target search directory does not exist")

        from multiprocessing.pool import ThreadPool
        query_list = list()
        for root, dirs, files in os.walk(search_dir):
            for file_name in files:
                query_list.append(os.path.join(root, file_name))

        pool = ThreadPool(thread_count)
        for result in pool.imap(
                lambda action: self.search_similar_file(action, limit),
                query_list
        ):
            yield result

class SimilarityTool:

    def __init__(self, file_name, word_tuple):
        self._src_info = {
            'file_name' : file_name,
            'word_tuple' : word_tuple
        }

    def exec_search(self, es, index, doc_type, limit):
        json_query = self._create_match_query(self._src_info['word_tuple'], limit)
        response = es.search(index=index, doc_type=doc_type, body=json_query, search_type='dfs_query_then_fetch')
        hits_hits = response['hits']['hits']
        hit_data_list = []
        for hit in hits_hits:
            hit_data_dic = {}
            hit_data_dic['_index'] = hit['_index']
            hit_data_dic['_type'] = hit['_type']
            hit_data_dic['_id'] = hit['_id']
            hit_data_dic['_score'] = hit['_score']
            _source_data = es.get(hit['_index'], hit['_type'], hit['_id'])['_source']
            hit['_ssdeep'] = "{}:{}:{}".format(_source_data["chunk_size"], _source_data["chunk"], _source_data["double_chunk"])
            origin_ssdeep = "{}:{}:{}".format(self._src_info['word_tuple'][0], self._src_info['word_tuple'][1], self._src_info['word_tuple'][2])
            ssdeep_similarity = ssdeep.compare(origin_ssdeep, hit['_ssdeep'])
            hit_data_dic['similarity'] = ssdeep_similarity
            hit_data_list.append(hit_data_dic)
        return hit_data_list

    def _create_match_query(self, src_word_tuple, limit):
        chunk_size = int(src_word_tuple[0])
        chunk = src_word_tuple[1]
        double_chunk = src_word_tuple[2]
        query = {
            "_source": False,
            "explain": False,
            "size": limit,
            "query": {
                "bool": {
                    "should": [
                        {
                            "bool": {
                                "must": [
                                    {
                                        "term": {
                                            "chunk_size": str(chunk_size)
                                        }
                                    },
                                    {
                                        "bool": {
                                            "should": [
                                                {
                                                    "match": {
                                                        "chunk": {
                                                            "query": chunk
                                                        }
                                                    }
                                                }
                                            ],
                                            "minimum_should_match": 1
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "bool": {
                                "must": [
                                    {
                                        "term": {
                                            "chunk_size": str(chunk_size)
                                        }
                                    },
                                    {
                                        "bool": {
                                            "should": [
                                                {
                                                    "match": {
                                                        "double_chunk": {
                                                            "query": double_chunk
                                                        }
                                                    }
                                                }
                                            ],
                                            "minimum_should_match": 1
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "bool": {
                                "must": [
                                    {
                                        "term": {
                                            "chunk_size": str(chunk_size / 2)
                                        }
                                    },
                                    {
                                        "bool": {
                                            "should": [
                                                {
                                                    "match": {
                                                        "double_chunk": {
                                                            "query": chunk
                                                        }
                                                    }
                                                }
                                            ],
                                            "minimum_should_match": 1
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "bool": {
                                "must": [
                                    {
                                        "term": {
                                            "chunk_size": str(chunk_size * 2)
                                        }
                                    },
                                    {
                                        "bool": {
                                            "should": [
                                                {
                                                    "match": {
                                                        "chunk": {
                                                            "query": double_chunk
                                                        }
                                                    }
                                                }
                                            ],
                                            "minimum_should_match": 1
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }
        json_query = json.dumps(query)
        return json_query

    def get_report(self, similar_report):
        report =  { 'query' : self._src_info['file_name'], 'similar_files' : list() }
        for hit in similar_report:
            hit_report = {
                '_id' : hit['_id'],
                '_score' : hit['_score'],
                'similarity' : hit['similarity'],
            }
            report['similar_files'].append(hit_report)
        return report

def preprocess_func(file_path):
    if not file_path.split('.')[-1] == 'vir':
        raise BaseException("Not .vir file")
    data = load_preprocessed_data(file_path)
    return data


def load_preprocessed_data(file_path):
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
        ssdeep_hash = ssdeep.hash(file_bytes)
        chunk_size = ssdeep_hash.split(':')[0]
        chunk = ssdeep_hash.split(':')[1]
        double_chunk = ssdeep_hash.split(':')[2]
    return chunk_size, chunk, double_chunk