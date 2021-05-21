import os
import hashlib
from multiprocessing import freeze_support
from multiprocessing.pool import Pool
from functools import partial
from tqdm import tqdm
from museum.module import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_file_md5(file_path):
    with open(file_path, 'rb') as f:
        bytes_data = f.read()
    return hashlib.md5(bytes_data).hexdigest()


def module_loader(module_info):
    module_name = module_info['module_name']
    klass = globals()[module_name]
    module = klass(**module_info['module_params'])
    return module


def hit_word_parser(hit):
    hit_word_list = list()
    explanation = hit['_explanation']
    bfs_q = [explanation]
    explanation['visited'] = True
    while len(bfs_q):
        cur_node = bfs_q.pop(0)
        if 'weight(' in cur_node['description']:
            hit_word_list.append(cur_node['description'].split(':')[1].split(' ')[0])
            continue
        if 'details' in cur_node:
            for adj_node in cur_node['details']:
                if 'visited' not in adj_node:
                    adj_node['visited'] = True
                    bfs_q.append(adj_node)
    return set(hit_word_list)


def walk_directory(target_dir):
    file_list = list()
    for root, dirs, files in os.walk(target_dir):
        for file_name in files:
            file_list.append(os.path.join(root, file_name))
    return file_list


def get_file_name(file_path):
    return os.path.splitext(os.path.split(file_path)[1])[0]


def batch_generator(file_list, batch_size):
    if batch_size:
        batch_jobs = []
        if len(file_list) % batch_size:
            batch_count = len(file_list) // batch_size + 1
        else:
            batch_count = len(file_list) // batch_size + 1
        for i in range(batch_count):
            batch_jobs.append(file_list[i * batch_size:(i + 1) * batch_size])
    else:
        batch_jobs = [file_list]
    for batch_job in batch_jobs:
        yield batch_job


def mp_helper(worker, jobs, process_count=8, **kwargs):
    with Pool(processes=process_count) as pool:
        for ret in pool.imap(partial(worker, **kwargs), jobs):
            yield ret
