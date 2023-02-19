import json


def get_bulk_request(md5, samples, num_chunks, file_name, index_name):
    header = {'index': {"_index": index_name, '_id': md5}}
    body = {
        'data': list(samples),
        'num_chunks': num_chunks,
        'file_name': file_name
    }
    return json.dumps(header)+'\n'+json.dumps(body)


def get_search_query(samples):
    query = {
        "bool": {
            "should": [
                {"term": {"data": sample}} for sample in samples
            ]
        }
    }
    return query


def get_exists_request(index_name, md5):
    header = {'index': index_name, 'search_type': 'dfs_query_then_fetch'}
    body = {
        "_source": False,
        "query": {
            "ids": {
                "values": md5
            }
        }
    }
    return json.dumps(header)+'\n'+json.dumps(body)


def get_msearch_request(index_name, samples, limit):
    header = {'index': index_name, 'search_type': 'dfs_query_then_fetch'}
    body = {
        "_source": True,
        "explain": True,
        "size": limit,
        "query": {
            "bool": {
                "should": [
                    {"term": {"data": sample}} for sample in samples
                ]
            }
        }
    }
    return json.dumps(header)+'\n'+json.dumps(body)


def get_settings(interval=10, shards=5, replicas=1):
    return {
        "refresh_interval": f'{interval}s',
        'number_of_shards': shards,
        'number_of_replicas': replicas,
        "similarity": {
            "scripted_one": {
                "type": "scripted",
                "script": {
                    "source": "return 1;"
                }
            }
        }
    }


def get_mappings(module_name, module_params, num_hash, use_smallest, use_mod, use_minmax):
    return {
        '_meta': {
            'module_info': {
                'module_name': module_name,
                'module_params': module_params
            },
            'num_hash': num_hash,
            'use_smallest': use_smallest,
            'use_mod': use_mod,
            'use_minmax': use_minmax,
        },
        "dynamic": "strict",
        "properties": {
            'data': {
                'type': 'keyword',
                'similarity': 'scripted_one'
            },
            'num_chunks': {
                'type': 'integer'
            },
            'file_name': {
                'type': 'keyword'
            }
        }
    }
