def get_document_dict(name, index, min_hashes, feature_size):
    doc = {
        "_index": index,
        "_type": '_doc',
        "_id": name,
        "_source": {
            'data': min_hashes,
            'feature_size': feature_size
        }
    }
    return doc


def create_query(min_hashes, limit):
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


def get_mapping_form(shards, replicas, use_k_smallest, hash_count, module_name, use_mod, use_minmax, module_params):
    module_kwargs = dict()
    if type(module_params) == dict:
        for k, v in module_params.items():
            module_kwargs[k] = v

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
                    'module': module_name,
                    'hash_count': hash_count,
                    'k-smallest': use_k_smallest,
                    'use_mod': use_mod,
                    'use_minmax': use_minmax,
                    'module_kwargs': module_kwargs,
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

