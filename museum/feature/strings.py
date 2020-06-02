import re, pickle
from hashlib import sha256

MAX_FILESIZE = 16 * 1024 * 1024
MAX_STRINGCNT = 2048
MAX_STRINGLEN = 1024


def preprocess_func(file_path, **kwargs):
    with open(file_path, "rb") as f :
        data = f.read(MAX_FILESIZE)
    strings = re.findall(b"[\x1f-\x7e]{6,}", data)
    for idx, s in enumerate(strings):
        strings[idx] = s.decode('ascii')
    for s in re.findall(b"(?:[\x1f-\x7e][\x00]){6,}", data):
        strings.append(s.decode('utf-16le'))
    strings = strings[:MAX_STRINGCNT]
    for idx, s in enumerate(strings):
        strings[idx] = s[:MAX_STRINGLEN]
    return set(strings)

def sha256bit_to_x_bit(sha256_byte, only_use_bit_size):
    sha256_byte = int.from_bytes(sha256_byte, byteorder='big', signed=False)
    cutting_bit_result = sha256_byte >> 256 - only_use_bit_size
    final_result = hex(cutting_bit_result)[2:]
    final_result = final_result.rjust(int(only_use_bit_size / 4), '0')
    return final_result
