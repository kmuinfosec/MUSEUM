import time

from museum import api


if __name__ == '__main__':
    es_host = 'http://localhost:9200'
    index_dir = r'C:\index_dir'
    search_dir = r'C:\search_dir'
    search_file = r'C:\test.pdf'
    index_name = 'test'

    # api.delete_index(es_host, index_name)
    api.create_index(es_host, index_name, 'ae', module_params={'window_size': 128}, num_hash=64)
    api.bulk(es_host, index_name, index_dir, process=2)
    time.sleep(6)

    for report_list in api.msearch(es_host, index_name, search_dir, limit=1, process=2, disable_tqdm=True):
        for report in report_list:
            print(report)

    report = api.search(es_host, index_name, search_file)
    print(report)
