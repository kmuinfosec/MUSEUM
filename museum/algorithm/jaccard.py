"""
- r_e : estimated resemblance (k-smallest)
    = |M(A) ∩ M(B) ∩ MINs(M(A) U M(B))| / |MINs(M(A) U M(B))| 
- r_e : estimated resemblance (k-independent)
    = |M(A) ∩ M(B)| / k 
"""


def estimated_similarity(sampled_query, sampled_index, hit_samples, index_meta):
    sample_union = sampled_query | sampled_index
    min_union = set(sorted(list(sample_union), key=lambda x: int(x, 16))[:min(len(sample_union), index_meta['num_hash'])])
    if index_meta['use_smallest']:
        similarity = len(hit_samples & min_union) / len(min_union)
    elif index_meta['use_minmax']:
        similarity = len(hit_samples) / index_meta['num_hash'] * 2
    else:
        similarity = len(hit_samples) / index_meta['num_hash']
    return similarity


"""
- c_e : estimated containment
    = (r_e * (|A| + |B|)) / min(|A|,|B|) * (r_e + 1) 
"""


def estimated_containment(e_s, query_feature_size, index_feature_size):
    min_len = min(query_feature_size, index_feature_size)
    containment = (e_s * (query_feature_size + index_feature_size)) / (min_len * (e_s + 1))
    return containment
