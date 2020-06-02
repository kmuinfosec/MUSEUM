from museum import Museum
import time


INDEX_DIR = r''
SEARCH_DIR = r''
INDEX_NAME = 'test'
ES_HOST = '127.0.0.1'
ES_PORT = 9200

if __name__ == '__main__':
    ms = Museum(host=ES_HOST, port=ES_PORT)
    ms.create_index(INDEX_NAME,  module_name='strings', hash_count=128, use_k_smallest=True, use_minmax=False, use_mod=0, shards=3, replicas=1, module_kwargs={})

    start_time = time.time()
    ms.insert_bulk(INDEX_NAME, INDEX_DIR, process_count=8, use_caching=True)

    time.sleep(35) # wait for indexing to finish

    for report in ms.search_bulk(INDEX_NAME, SEARCH_DIR, limit=1, process_count=8, use_caching=True, tqdm_disable=False):
        ############################
        # TODO: Process the report
        ############################
        pass
