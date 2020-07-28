import os
import hashlib
import json


def preprocess_func(file_path, **kwargs):
    if 'window_size' not in kwargs:
        msg = "'window_size' parameter is not passed"
        raise Exception(msg)
    if not os.path.isfile(file_path):
        error_msg = "{} does not exist".format(file_path)
        raise Exception(error_msg)
    window_size = kwargs['window_size']
    md5 = os.path.splitext(os.path.split(file_path)[1])[0]
    with open(file_path, 'r') as f:
        apics = json.load(f)[md5]
    chunk_list = []
    if not len(apics):
        return chunk_list
    for api_call in apics:
        chunk_list.append(apics_ae(api_call, window_size))
    chunk_set = set()
    for chunk in chunk_list:
        for element in chunk:
            chunk_set.add(element)
    return list(chunk_set)


def apics_ae(api_call, window_size):
    chunk_list = []
    idx = 0
    call_list = []
    int_api_call = []
    for api in api_call:
        int_api_call.append(int(hashlib.md5(api.encode()).hexdigest(), 16))
    # this while for all file content
    while idx < len(api_call):
        # ae chunking algorithm section
        max_value = int_api_call[idx]
        max_position = idx
        call_list.append(api_call[idx])
        idx += 1
        while idx < len(api_call):
            if int_api_call[idx] <= max_value:
                if idx == max_position + window_size:
                    concat_call_list = ''.join(call_list)
                    chunk_list.append(concat_call_list)
                    call_list = []
                    idx += 1
                    break
            else:
                max_value = int_api_call[idx]
                max_position = idx
            call_list.append(api_call[idx])
            idx += 1
    if len(call_list):
        concat_call_list = ''.join(call_list)
        chunk_list.append(concat_call_list)
    return chunk_list
