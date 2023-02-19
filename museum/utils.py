from multiprocessing import pool, freeze_support
from functools import partial
from typing import List
import os
import hashlib


def get_file_md5(file_path: str) -> str:
    with open(file_path, 'rb') as f:
        bytes_data = f.read()
    return hashlib.md5(bytes_data).hexdigest()


def get_bytes_md5(file_bytes: bytes) -> str:
    return hashlib.md5(file_bytes).hexdigest()


def hit_word_parser(hit) -> set:
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


def walk_directory(dir_path: str) -> List[str]:
    path_list = list()
    for root, dirs, files in os.walk(dir_path):
        for file_name in files:
            path_list.append(os.path.join(root, file_name))
    return path_list


def batch_generator(path_list: List[str], batch_size=10000) -> List[str]:
    num_batch = len(path_list) // batch_size + 1 if len(path_list) % batch_size else len(path_list) // batch_size
    for batch_idx in range(num_batch):
        yield path_list[batch_idx * batch_size:(batch_idx + 1) * batch_size]


def mp(worker, jobs, process_count, **kwargs):
    freeze_support()
    with pool.Pool(processes=process_count) as p:
        for ret in p.imap(partial(worker, **kwargs), jobs):
            yield ret
