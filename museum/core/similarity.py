from museum.util import hit_word_parser


"""
- numerator = |MINs(M(A) U M(B)) ∩ M(A) ∩ M(B)|
- denominator = |MINs(M(A) U M(B))|
- es : estimated similarity 
    = numerator / denominator (k-independent)
    = |M(A) ∩ M(B)| / k (k-smallest)
- ej : estimated containment
    = (es * (|A| + |B|)) / min(|A|,|B|) * (es+1) 
"""


def get_similarity(min_hashes, response, feature_size, index_info):
    min_hashes = set(min_hashes)
    result_list = []
    for hit in response['hits']['hits']:
        hit_source = set(hit['_source']['data'])
        if 'feature_size' in hit['_source']:
            hit_feature_size = hit['_source']['feature_size']
        intersect = hit_word_parser(hit)
        union = list(set(min_hashes) | hit_source)
        for i, num in enumerate(union):
            change_octal = int(num, 16)
            union[i] = change_octal
        sorted_union = sorted(union)
        min_union = set()
        for i in range(min(len(sorted_union), index_info['hash_count'])):
            min_union.add(hex(sorted_union[i])[2:].rjust(32, '0'))
        numerator = min_union & intersect
        if index_info['use_smallest']:
            es = len(numerator) / min(len(sorted_union), index_info['hash_count'])
        else:
            if index_info['use_minmax']:
                es = len(intersect) / max(len(min_hashes), len(hit_source))
            else:
                es = len(intersect) / index_info['hash_count']
        if feature_size in hit['_source']:
            min_len = min(feature_size, hit_feature_size)
            ec = (es * (feature_size + hit_feature_size)) / (min_len * (es + 1))
        else:
            ec = None
        result_list.append({
            '_id': hit['_id'],
            '_score': hit['_score'],
            'e_similarity': es,
            'e_containment': ec
        })
    return result_list
