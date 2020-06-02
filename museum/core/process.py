from museum.util import module_check, load_pickle, save_pickle, load_preprocessed_data
from museum.core.minhash import get_min_hashes
import importlib
import hashlib
import os


def preprocess(file_path, use_k_smallest, hash_count, module_name, use_mod, use_minmax, module_kwargs):
    if module_name is None:
        feature_set = load_preprocessed_data(file_path)
    else:
        module_check(module_name)
        module_name = 'museum.feature.'+module_name
        preprocess_module = importlib.import_module(module_name)
        feature_set = preprocess_module.preprocess_func(file_path, **module_kwargs)
    feature_size = len(feature_set)
    if use_mod != 0:
        feature_set = reduce_the_feature_by_mod(feature_set, use_mod)
    min_hashes = get_min_hashes(feature_set, hash_count, use_k_smallest, use_minmax)
    return min_hashes, feature_size


def reduce_the_feature_by_mod(feature, mod_num):
    after_mod_list = []
    feature_list = list(set(feature))
    for feature in feature_list:
        hashed_feature = int(hashlib.md5(feature).hexdigest(), 16)
        if hashed_feature % mod_num == 0:
            after_mod_list.append(feature)
    return after_mod_list

