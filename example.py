from museum.client import Museum
from museum.feature import AsymmetricExtremum, Strings
import time


INDEX_DIR = r'D:\VirusSign\20181001'
SEARCH_DIR = r'D:\VirusSign\20181002_3000'
INDEX_NAME = 'test2'
ES_HOST = '203.246.112.139'
ES_PORT = 29200

if __name__ == '__main__':
    ms = Museum(host=ES_HOST, port=ES_PORT)

    ms.create_index(INDEX_NAME, AsymmetricExtremum(window_size=128), hash_count=128, use_smallest=True)
    ms.insert_bulk(INDEX_NAME, INDEX_DIR, process_count=8, use_caching=True)

    # wait for indexing to finish
    time.sleep(35)

    for report in ms.search_bulk(INDEX_NAME, SEARCH_DIR, limit=1, process_count=8, use_caching=True):
        ############################
        # TODO: Process the report
        ############################
        pass
