import os
import pickle
from multiprocessing import freeze_support
from multiprocessing.pool import Pool, ThreadPool
from functools import partial
from tqdm import tqdm
USER_HOME = os.path.expanduser('~')
CACHE_DIR = os.path.join(USER_HOME, 'museum_cache')
if not os.path.isdir(CACHE_DIR):
    os.mkdir(CACHE_DIR)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def module_check(module):
    module_path = os.path.join(os.path.join(BASE_DIR, 'feature'), module+'.py')
    if not os.path.isfile(module_path):
        error_msg = "'{}' feature module doesn't exist".format(module)
        raise ModuleNotFoundError(error_msg)


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


def load_pickle(file_path):
    with open(file_path, 'rb') as f:
        pickle_data = pickle.load(f)
    return pickle_data


def save_pickle(obj, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(obj, f)


def walk_directory(target_dir):
    file_list = list()
    for root, dirs, files in os.walk(target_dir):
        for file_name in files:
            file_list.append(os.path.join(root, file_name))
    return file_list


def get_file_name(file_path):
    return os.path.splitext(os.path.split(file_path)[1])[0]


def check_cached(file_path, use_smallest, hash_count, module_name, use_minmax):
    target_dir, target_file = os.path.split(file_path)
    root_dir, last_dir = os.path.split(target_dir)
    if module_name is None:
        module_str = ''
    else:
        module_str = '_'+module_name
    if use_smallest:
        prefix = 'fast'
    elif use_minmax:
        prefix = 'minmax'
    else:
        prefix = 'slow'
    cached_dir = os.path.join(CACHE_DIR, '('+prefix+str(hash_count)+module_str+')'+last_dir)
    cached_path = os.path.join(cached_dir, os.path.splitext(target_file)[0]+'.dat')
    if os.path.isdir(cached_dir):
        if os.path.isfile(cached_path):
            return True, cached_path
    return False, file_path


def load_cached_data(file_path):
    cached_data = load_pickle(file_path)
    min_hashes, feature_size = cached_data[0], cached_data[1]
    return min_hashes, feature_size


def caching(min_hashes, feature_size, file_path, use_smallest, hash_count, module_name, use_minmax):
    file_dir, file_name = os.path.split(file_path)
    root_dir, last_dir = os.path.split(file_dir)
    if module_name is None:
        module_str = ''
    else:
        module_str = '_'+module_name
    if use_smallest:
        prefix = 'fast'
    elif use_minmax:
        prefix = 'minmax'
    else:
        prefix = 'slow'
    cache_dir = os.path.join(CACHE_DIR, '('+prefix+str(hash_count)+module_str+')')+last_dir
    cache_path = os.path.join(cache_dir, os.path.splitext(file_name)[0]+'.dat')
    if not os.path.isdir(cache_dir):
        os.mkdir(cache_dir)
    save_pickle((min_hashes, feature_size), cache_path)


def multi_threading(worker, jobs, process_count, **kwargs):
    with ThreadPool(processes=process_count) as pool:
        for ret in tqdm(pool.imap(partial(worker, **kwargs), jobs), total=len(jobs), desc=worker.__name__):
            yield ret


def get_batch_list(file_list, batch_size):
    file_count = len(file_list)
    batch_list = []
    if batch_size is not None:
        batch_count = file_count // batch_size + 1 if file_count % batch_size else file_count // batch_size
        for i in range(batch_count):
            batch_list.append(file_list[i * batch_size:(i + 1) * batch_size])
    else:
        batch_list = [file_list]
    return batch_list


def load_preprocessed_data(file_path):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    return list(set(data))

