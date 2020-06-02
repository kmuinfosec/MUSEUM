from museum.util import module_loader, check_cached, load_cached_data, caching
from museum.core.minhash import get_min_hashes

import hashlib
import os

def preprocess(file_path, index_info, use_caching=False):
    name = os.path.splitext(os.path.split(file_path)[1])[0]
    is_cached, target_file = check_cached(file_path, index_info)
    if is_cached:
        min_hashes, feature_size = load_cached_data(target_file)
    else:
        min_hashes, feature_size = module_process(file_path, index_info)
        if use_caching:
            caching(min_hashes, feature_size, target_file, index_info)
    return min_hashes, feature_size, name

def module_process(file_path, index_info):
    module = module_loader(index_info['module_info'])
    feature_set = module.process(file_path)
    feature_size = len(feature_set)
    if index_info['use_mod']:
        feature_set = reduce_the_feature_by_mod(feature_set, index_info['use_mod'])
    min_hashes = get_min_hashes(feature_set, index_info['hash_count'], index_info['use_smallest'], index_info['use_minmax'])
    return min_hashes, feature_size

def reduce_the_feature_by_mod(feature, mod_num):
    after_mod_list = []
    feature_list = list(set(feature))
    for feature in feature_list:
        hashed_feature = int(hashlib.md5(feature).hexdigest(), 16)
        if hashed_feature % mod_num == 0:
            after_mod_list.append(feature)
    return after_mod_list

