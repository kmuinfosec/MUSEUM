import os
import pickle
from multiprocessing import freeze_support
from multiprocessing.pool import Pool, ThreadPool
from functools import partial
from tqdm import tqdm
from museum.feature import *

USER_HOME = os.path.expanduser('~')
CACHE_DIR = os.path.join(USER_HOME, 'museum_cache')
if not os.path.isdir(CACHE_DIR):
    os.mkdir(CACHE_DIR)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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

def get_cache_path(file_path, index_info):
    root, target_file = os.path.split(file_path)
    root_dir, target_dir = os.path.split(root)
    id_str = '('
    if index_info['use_smallest']:
        id_str += 'smallest'
    elif index_info['use_minmax']:
        id_str += 'minmax'
    else:
        id_str += 'normal'
    id_str += str(index_info['hash_count'])+'_'+index_info['module_info']['module_name']+')'
    cache_dir = os.path.join(CACHE_DIR, id_str+target_dir)
    cache_file_path = os.path.join(cache_dir, os.path.splitext(target_file)[0]+'.dat')
    return cache_file_path

def check_cached(file_path, index_info):
    cache_file_path = get_cache_path(file_path, index_info)
    if os.path.isdir(os.path.split(cache_file_path)[0]):
        if os.path.isfile(cache_file_path):
            return True, cache_file_path
    return False, file_path


def load_cached_data(file_path):
    cached_data = load_pickle(file_path)
    min_hashes, feature_size = cached_data[0], cached_data[1]
    return min_hashes, feature_size


def caching(min_hashes, feature_size, file_path, index_info):
    cache_path = get_cache_path(file_path, index_info)
    cache_dir = os.path.split(cache_path)[0]
    if not os.path.isdir(cache_dir):
        os.mkdir(cache_dir)
    save_pickle((min_hashes, feature_size), cache_path)

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

def multiprocessing_helper(worker, jobs, process_count=8, tqdm_disable=False, **kwargs):
    with Pool(processes=process_count) as pool:
        for ret in tqdm(pool.imap(partial(worker, **kwargs), jobs),
                        total=len(jobs), desc=worker.__name__, disable=tqdm_disable):
            yield ret

def multithreading_helper(worker, jobs, process_count, **kwargs):
    with ThreadPool(processes=process_count) as pool:
        for ret in tqdm(pool.imap(partial(worker, **kwargs), jobs), total=len(jobs), desc=worker.__name__):
            yield ret

    # @staticmethod
    # def _parallel_call(params, **kwargs):  # a helper for calling 'remote' instances
    #     cls = getattr(sys.modules[__name__], params[0])  # get our class type
    #     instance = cls.__new__(cls)  # create a new instance without invoking __init__
    #     instance.__dict__ = params[1]  # apply the passed state to the new instance
    #     setattr(instance, 'es', Elasticsearch(hosts=params[1]['host'], port=params[1]['port'], timeout=600))
    #     method = getattr(instance, params[2])  # get the requested method
    #     args = params[3] if isinstance(params[3], (list, tuple)) else [params[3]]
    #     return method(*args, **kwargs)  # expand arguments, call our method and return the result
    #
    # def _prepare_call(self, name, args):
    #     for arg in args:
    #         instance_property = self.__dict__.copy()
    #         del instance_property['es']
    #         yield [self.__class__.__name__, instance_property, name, arg]
