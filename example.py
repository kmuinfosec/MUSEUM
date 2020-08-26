from museum import MUSEUM
from museum.module.ae import AsymmetricExtremum
import time


INDEX_DIR = r'D:\VirusSign\20181001'
SEARCH_DIR = r'D:\VirusSign\20181002_3000'
INDEX_NAME = 'test4'
ES_HOST = '203.246.112.139'
ES_PORT = 29200

if __name__ == '__main__':
    ms = MUSEUM(host=ES_HOST, port=ES_PORT, use_caching=False)

    ms.create_index(INDEX_NAME, AsymmetricExtremum(window_size=128), num_hash=128, use_smallest=True)
    ms.bulk_index(INDEX_NAME, INDEX_DIR, process_count=8,)

    # wait for indexing to finish
    time.sleep(11)

    for report_list in ms.multi_search(INDEX_NAME, SEARCH_DIR, limit=1, process_count=8):
        ############################
        # TODO: Process the report
        ############################
        for report in report_list:
            print(report)
        input()
        pass
