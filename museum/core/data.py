def get_document_dict(preprocess_items, index_name):
    document = {
        "_index": index_name,
        "_id": preprocess_items[0],
        "_source": {
            'data': preprocess_items[1],
            'feature_size': preprocess_items[2],
            'file_name': preprocess_items[3]
        }
    }
    return document


def get_query_dict(min_hashes, limit):
    if min_hashes is not None:
        query = {
            "_source": True,
            "explain": True,
            "size": limit,
            "query": {
                "bool": {
                    "should": [
                        {"term": {"data": min_hash}} for min_hash in min_hashes
                    ]
                }
            }
        }
        return query


def get_mapping_dict(module, num_hash, use_smallest, use_mod, use_minmax, shards, replicas):
    module_info = {
        'module_name': module.__class__.__name__,
        'module_params': module.__dict__
    }
    mapping_dict = {
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
                'module_info': module_info,
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
    return mapping_dict

