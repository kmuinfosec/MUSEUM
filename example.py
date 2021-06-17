from museum import MUSEUM
from museum.module import AsymmetricExtremum


INDEX_DIR = r'D:\indexDir'
SEARCH_DIR = r'C:\searchDir'
INDEX_NAME = 'test'
ES_HOST = 'localhost'
ES_PORT = 9200

if __name__ == '__main__':
    ms = MUSEUM(host=ES_HOST, port=ES_PORT, use_caching=False)

    ms.create_index(INDEX_NAME, AsymmetricExtremum(window_size=128), num_hash=128)
    ms.bulk(INDEX_NAME, INDEX_DIR, process_count=8)

    for report_list in ms.multi_search(INDEX_NAME, SEARCH_DIR, limit=1, process_count=8):
        ############################
        # TODO: Process the report
        ############################
        for report in report_list:
            print(report)
        input()
