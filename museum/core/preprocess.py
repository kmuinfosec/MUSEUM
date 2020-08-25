import os
import hashlib

from museum.utils import cache, module_loader, get_file_md5


def do(file_path, index_info, use_caching):
    file_md5 = get_file_md5(file_path)
    file_name = os.path.splitext(os.path.split(file_path)[1])[0]
    is_cache, cache_path = cache.check_cached(file_md5, index_info)
    if is_cache:
        min_hashes, feature_size = cache.load_cache(cache_path)
    else:
        module = module_loader(index_info['module_info'])
        feature_set = module.process(file_path)
        feature_size = len(feature_set)
        if index_info['use_mod']:
            feature_set = reduce_the_feature_by_mod(feature_set, index_info['use_mod'])
        min_hashes = minhash(feature_set, index_info['num_hash'], index_info['use_smallest'], index_info['use_minmax'])
        if use_caching:
            cache.make_cache(cache_path, min_hashes, feature_size)
    return file_md5, min_hashes, feature_size, file_name


def minhash(feature_set, num_hash, use_smallest, use_min_max):
    feature_list = list(feature_set)
    if len(feature_list) <= 1:
        return
    if use_smallest:
        min_hashes = k_smallest(feature_list, num_hash)
    else:
        min_hashes = k_independent(feature_list, num_hash, use_min_max)
    return list(set(min_hashes))


def k_smallest(feature_list, num_hash):
    int_features = []
    feature_type = type(feature_list[0])
    if feature_type == bytes:
        for i in range(len(feature_list)):
            hashed_feature = hashlib.md5(feature_list[i]).hexdigest()
            int_features.append(int(hashed_feature, 16))
    else:
        for i in range(len(feature_list)):
            hashed_feature = hashlib.md5(feature_list[i].encode()).hexdigest()
            int_features.append(int(hashed_feature, 16))
    int_features = list(set(int_features))
    int_features.sort()
    min_hashes = []
    num_min = min(num_hash, len(int_features))
    for i in range(num_min):
        insert_feature = hex(int_features[i])[2:].rjust(32, '0')
        min_hashes.append(insert_feature)
    return min_hashes


def k_independent(feature_list, num_hash, use_min_max):
    min_hashes = []
    int_min_hashes = []
    for i in range(1, num_hash + 1):
        int_features = []
        feature_type = type(feature_list[0])
        if feature_type == bytes:
            for j in range(len(feature_list)):
                salt_feature = feature_list[j] + bytes(str(i).encode())
                hashed_feature = int(hashlib.md5(salt_feature).hexdigest(), 16)
                int_features.append(hashed_feature)
        else:
            for j in range(len(feature_list)):
                salt_feature = str(i) + str(i) + feature_list[j] + str(i) + str(i)
                hashed_feature = int(hashlib.md5(salt_feature.encode()).hexdigest(), 16)
                int_features.append(hashed_feature)

        int_features.sort()
        int_min_hashes.append(int_features[0])

        if use_min_max:
            int_min_hashes.append(int_features[-1])
    for int_min_hash in int_min_hashes:
        min_hashes.append(hex(int_min_hash)[2:].rjust(32, '0'))
    return min_hashes


def reduce_the_feature_by_mod(feature, mod_num):
    after_mod_list = []
    feature_list = list(set(feature))
    for feature in feature_list:
        hashed_feature = int(hashlib.md5(feature).hexdigest(), 16)
        if hashed_feature % mod_num == 0:
            after_mod_list.append(feature)
    return after_mod_list

