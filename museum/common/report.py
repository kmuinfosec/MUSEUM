from museum.algorithm.jaccard import estimated_similarity, estimated_containment
from museum.common.utils import hit_word_parser


def make_report_hits(response, query_samples, query_feature_size, index_info):
    hits_report = []
    for hit_doc in response['hits']['hits']:
        hit_id = hit_doc['_id']
        hit_score = hit_doc['_score']
        index_samples = set(hit_doc['_source']['data'])
        hit_samples = hit_word_parser(hit_doc)
        e_s = estimated_similarity(query_samples, index_samples, hit_samples, index_info)
        e_c = estimated_containment(e_s, query_feature_size, hit_doc['_source']['feature_size'])
        hits_report.append({
            '_id': hit_id, '_score': hit_score, 'file_name': hit_doc['_source']['file_name'],
            'estimated_similarity': e_s, 'estimated_containment': e_c
        })
    return hits_report
