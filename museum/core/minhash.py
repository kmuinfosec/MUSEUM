import hashlib


def get_min_hashes(feature_set, hash_count, use_k_smallest=False, use_min_max=False):
    feature_list = list(feature_set)
    if len(feature_list) <= 1:
        return
    if use_k_smallest:
        min_hashes = k_smallest_min_hashes(feature_list, hash_count)
    else:
        min_hashes = k_independent_min_hashes(feature_list, hash_count, use_min_max)
    return list(set(min_hashes))


def k_smallest_min_hashes(feature_list, hash_count):
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
    num_min = min(hash_count, len(int_features))
    for i in range(num_min):
        insert_feature = hex(int_features[i])[2:].rjust(32, '0')
        min_hashes.append(insert_feature)
    return min_hashes


def k_independent_min_hashes(feature_list, hash_count, use_min_max):
    min_hashes = []
    int_min_hashes = []
    for i in range(1, hash_count + 1):
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
