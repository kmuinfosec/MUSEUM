def create_document(preprocess_items, index_name):
    min_hashes, feature_size, name = preprocess_items
    if min_hashes is not None:
        document = {
            "_index": index_name,
            "_type": '_doc',
            "_id": name,
            "_source": {
                'data': min_hashes,
                'feature_size': feature_size
            }
        }
        return document

def create_query(preprocess_items, limit):
    min_hashes, feature_size, name = preprocess_items
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

def create_mapping_form(module, hash_count, use_smallest, use_mod, use_minmax, shards, replicas):
    module_info = {
        'module_name': module.__class__.__name__,
        'module_params': module.__dict__
    }
    mapping_dict = {
        "settings": {
            "refresh_interval": "30s",
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
            "_doc": {
                '_meta': {
                    'module_info': module_info,
                    'hash_count': hash_count,
                    'use_smallest': use_smallest,
                    'use_mod': use_mod,
                    'use_minmax': use_minmax,
                },
                "dynamic": "strict",
                "properties": {
                    'data': {
                        'type': 'text',
                        'similarity': 'scripted_one'
                    },
                    'feature_size': {
                        'type': 'integer'
                    }
                }
            }
        }
    }
    return mapping_dict

