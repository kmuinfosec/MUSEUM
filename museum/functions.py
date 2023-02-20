from museum.utils import get_file_md5, hit_word_parser
from typing import List, Set
from pathlib import Path
import hashlib
import importlib


def preprocess(file_path: Path, index_info: dict):

    module = importlib.import_module(f'museum.module.{index_info["module_info"]["module_name"]}')
    chunk_set = set(module.process(file_path, index_info['module_info']['module_params']))

    if index_info['use_mod']:
        chunk_set = modular_sampling(chunk_set, index_info['use_mod'])

    samples = minhash(chunk_set, index_info['num_hash'], index_info['use_smallest'], index_info['use_minmax'])
    return get_file_md5(file_path), samples, len(chunk_set), file_path.name


def minhash(chunk_set: Set[str], num_hash: int, use_smallest: bool, use_min_max: bool):
    chunk_list = list(chunk_set)
    if len(chunk_list) <= 1:
        return
    if use_smallest:
        samples = k_smallest(chunk_list, num_hash)
    else:
        samples = k_independent(chunk_list, num_hash, use_min_max)
    return set(samples)


def k_smallest(chunk_list: List[str], num_hash: int):
    int_chunks = []
    for chunk in chunk_list:
        if not type(chunk) == bytes:
            chunk = chunk.encode()
        int_chunks.append(int.from_bytes(hashlib.md5(chunk).digest(), 'big'))
    int_chunks = list(set(int_chunks))
    int_chunks.sort()
    samples = []
    minimum = min(num_hash, len(int_chunks))
    for i in range(minimum):
        samples.append(hex(int_chunks[i])[2:].rjust(32, '0'))
    return samples


def k_independent(chunk_list: List[str], num_hash: int, use_min_max: bool):
    samples = []
    int_samples = []
    for i in range(1, num_hash + 1):
        int_chunks = []
        for chunk in chunk_list:
            if not type(chunk) == bytes:
                chunk = chunk.encode()
            int_chunks.append(int.from_bytes(hashlib.md5(chunk+str(i).encode()).digest(), 'big'))
        int_chunks.sort()
        int_samples.append(int_chunks[0])
        if use_min_max:
            int_samples.append(int_chunks[-1])
    for int_sample in int_samples:
        samples.append(hex(int_sample)[2:].rjust(32, '0'))
    return samples


def modular_sampling(samples: Set[str], mod):
    sampled_set = set()
    samples = list(set(samples))
    for sample in samples:
        hashed_sample = int(hashlib.md5(sample).hexdigest(), 16)
        if hashed_sample % mod == 0:
            sampled_set.add(sample)
    return sampled_set


def estimated_jaccard_index(sampled_query, sampled_index, hit_samples, index_info):
    """
    - r_e : estimated resemblance (k-smallest)
        = |M(A) ∩ M(B) ∩ MINs(M(A) U M(B))| / |MINs(M(A) U M(B))|
    - r_e : estimated resemblance (k-independent)
        = |M(A) ∩ M(B)| / k
    """

    sample_union = sampled_query | sampled_index
    min_union = set(sorted(list(sample_union), key=lambda x: int(x, 16))[:min(len(sample_union), index_info['num_hash'])])
    if index_info['use_smallest']:
        similarity = len(hit_samples & min_union) / len(min_union)
    elif index_info['use_minmax']:
        similarity = len(hit_samples) / index_info['num_hash'] * 2
    else:
        similarity = len(hit_samples) / index_info['num_hash']
    return similarity


def estimated_containment(e_i, query_num_chunks, index_num_chunks):
    """
    - c_e : estimated containment
        = (r_e * (|A| + |B|)) / min(|A|,|B|) * (r_e + 1)
    """

    min_len = min(query_num_chunks, index_num_chunks)
    containment = (e_i * (query_num_chunks + index_num_chunks)) / (min_len * (e_i + 1))
    return containment


def get_hits_info(response, samples, num_chunks, index_info) -> List[dict]:
    hits_info = []
    for hit_doc in response['hits']['hits']:
        hit_id = hit_doc['_id']
        hit_score = hit_doc['_score']
        index_samples = set(hit_doc['_source']['data'])
        hit_samples = hit_word_parser(hit_doc)
        e_i = estimated_jaccard_index(samples, index_samples, hit_samples, index_info)
        e_c = estimated_containment(e_i, num_chunks, hit_doc['_source']['num_chunks'])
        hits_info.append({
            '_id': hit_id, '_score': hit_score, 'file_name': hit_doc['_source']['file_name'],
            'estimated_jaccard_index': e_i, 'estimated_jaccard_containment': e_c
        })
    return hits_info
