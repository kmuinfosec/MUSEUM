from hashlib import sha256
import pickle


def preprocess_func(file_path, use_bit_size):
    if not file_path.split('.')[-1] == 'ops':
        raise BaseException("Not .ops pickle file")
    data = load_preprocessed_data(file_path)
    if len(data) >= 1:
        oneDemensionList = []
        for func in range(len(data)):
            for basicBlock in range(len(data[func])):
                ops = ''
                for contents in range(len(data[func][basicBlock])):
                    ops += data[func][basicBlock][contents]
                ops = ops.encode('utf-8')  # string -> bytes
                sha256_chunk = sha256(ops).digest()
                sha256_chunk = sha256bit_to_x_bit(sha256_chunk, use_bit_size)
                oneDemensionList.append(sha256_chunk)
        if len(oneDemensionList) >= 1:
            return oneDemensionList
    return []

def load_preprocessed_data(file_path):
    with open(file_path, 'rb') as f:
        pickle_data = pickle.load(f)
    return pickle_data

def sha256bit_to_x_bit(sha256_byte, only_use_bit_size):
    sha256_byte = int.from_bytes(sha256_byte, byteorder='big', signed=False)
    cutting_bit_result = sha256_byte >> 256 - only_use_bit_size
    final_result = hex(cutting_bit_result)[2:]
    final_result = final_result.rjust(int(only_use_bit_size / 4), '0')
    return final_result