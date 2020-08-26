import json


def get_bulk_data(file_md5, samples, feature_size, file_name, index_name):
    header = {'index': {"_index": index_name, '_id': file_md5}}
    body = {
        'data': list(samples),
        'feature_size': feature_size,
        'file_name': file_name
    }
    return json.dumps(header)+'\n'+json.dumps(body)


def get_search_body(samples, limit):
    search_body = {
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
    return search_body


def get_multisearch_data(index_name, samples, limit):
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


def get_index_template(module, num_hash, use_smallest, use_mod, use_minmax, shards, replicas):
    index_template = {
        "settings": {
            "refresh_interval": "10s",
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
        },
        "mappings": {
            '_meta': {
                'module_info': {
                    'module_name': module.__class__.__name__,
                    'module_params': module.__dict__
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
                'feature_size': {
                    'type': 'integer'
                },
                'file_name': {
                    'type': 'keyword'
                }
            }
        }
    }
    return index_template

