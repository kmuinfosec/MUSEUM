import os
import hashlib
import json


def preprocess_func(file_path, **kwargs):
    if 'window_size' not in kwargs:
        msg = "'window_size' parameter is not passed"
        raise Exception(msg)
    if not os.path.isfile(file_path):
        error_msg = "{} does not exist".format(file_path)
        raise Exception(error_msg)
    window_size = kwargs['window_size']
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
    chunk_list = bytes_ae(file_bytes, window_size)
    return list(set(chunk_list))


def bytes_ae(byte_seq, window_size):
    bytes_len = len(byte_seq)
    chunk_bytes_list = []
    byte_idx = 0
    byte_arr = bytearray()
    # this while for all file content
    while byte_idx < bytes_len:
        # ae chunking algorithm section
        max_value = byte_seq[byte_idx]
        max_position = byte_idx
        byte_arr.append(byte_seq[byte_idx])
        byte_idx += 1
        while byte_idx < bytes_len:
            if byte_seq[byte_idx] <= max_value:
                if byte_idx == max_position + window_size:
                    content_bytes = bytes(byte_arr)
                    chunk_bytes_list.append(content_bytes)
                    byte_arr = bytearray()
                    byte_idx += 1
                    break
            else:
                max_value = byte_seq[byte_idx]
                max_position = byte_idx
            byte_arr.append(byte_seq[byte_idx])
            byte_idx += 1
    if len(byte_arr):
        content_bytes = bytes(byte_arr)
        chunk_bytes_list.append(content_bytes)
    return chunk_bytes_list
