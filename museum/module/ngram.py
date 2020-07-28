import os, pickle
import json

def preprocess_func(file_path, **kwargs):
    if 'n' not in kwargs:
        msg = "'n' parameter is not passed"
        raise Exception(msg)
    if not os.path.isfile(file_path):
        error_msg = "{} does not exist".format(file_path)
        raise BaseException(error_msg)
    n = kwargs['n']
    if 'is_api' in kwargs and kwargs['is_api']:
        md5 = os.path.splitext(os.path.split(file_path)[1])[0]
        with open(file_path, 'r') as f:
            apics = json.load(f)[md5]
        chunk_list = []
        if not len(apics):
            return chunk_list
        for api_call in apics:
            for i in range(len(api_call)-n+1):
                chunk_list.append(''.join(api_call[i:i+n]))
    else:
        with open(file_path, 'rb') as f:
            data = f.read()
        chunk_list = []
        for i in range(len(data)-n+1):
            chunk_list.append(data[i:i+n])
    return set(chunk_list)
