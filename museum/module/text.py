import os, pickle


def preprocess_func(file_path):
    if not os.path.isfile(file_path):
        error_msg = "{} does not exist".format(file_path)
        raise BaseException(error_msg)
    with open(file_path, 'r') as f:
        file_bytes = f.read()

    word_set = set()
    for word in file_bytes.split():
        word_set.add(word.encode())

    return word_set