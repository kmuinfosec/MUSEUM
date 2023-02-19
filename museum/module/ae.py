from museum.cext import ae_chunking


def process(file_path: str, module_params):
    chunk_list = ae_chunking(file_path, module_params['window_size'])
    return chunk_list


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
