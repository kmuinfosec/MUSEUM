from museum.core.feature import Base
import os
import ctypes
import platform


def check_arguments(file_path, file_bytes):
    if file_path is None and file_bytes is None:
        raise AttributeError("Please enter either file_path or file_bytes")
    if file_path is not None and not os.path.isfile(file_path):
        error_msg = "{} does not exist".format(file_path)
        raise FileNotFoundError(error_msg)


def get_library_path():
    module_base_path = os.path.dirname(os.path.abspath(__file__))
    lib_path = None
    if 'Windows' == platform.system():  # 윈도우 운영체제에서 c 모듈 로드
        if platform.architecture()[0] == '64bit':
            lib_path = os.path.join(module_base_path, 'ae_64bit_windows.dll')
        elif platform.architecture()[0] == '32bit':
            lib_path = os.path.join(module_base_path, 'ae_32bit_windows.dll')
    elif 'Linux' == platform.system():  # 리눅스 운영체제에서 c 모듈 로드
        if platform.architecture()[0] == '64bit':
            lib_path = os.path.join(module_base_path, 'ae_64bit_linux.so')
    if lib_path is None:
        raise OSError()
    return lib_path


def get_ae_chunking_func(ae_lib, file_path, file_bytes):
    if file_path is not None:
        ae_chunking = ae_lib.ae_chunking_from_path
        ae_chunking.argtypes = (
            ctypes.c_char_p, ctypes.POINTER(ctypes.POINTER(ctypes.c_uint)), ctypes.c_uint
        )
    else:
        ae_chunking = ae_lib.ae_chunking_from_bytes
        ae_chunking.argtypes = (
            ctypes.c_char_p, ctypes.c_uint, ctypes.POINTER(ctypes.POINTER(ctypes.c_uint)), ctypes.c_uint
        )
    ae_chunking.restype = ctypes.c_uint
    return ae_chunking


def get_release_func(ae_lib):
    release = ae_lib.release
    release.argtypes = [ctypes.POINTER(ctypes.c_uint)]
    release.restype = None
    return release


class AsymmetricExtremum(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'window_size' not in self.__dict__:
            msg = "Parameter 'window_size' must be passed"
            raise Exception(msg)
        self.window_size = self.__dict__['window_size']

    def process(self, file_path=None, file_bytes=None):
        check_arguments(file_path, file_bytes)
        ae_lib = ctypes.CDLL(get_library_path())
        ae_chunking_func = get_ae_chunking_func(ae_lib, file_path, file_bytes)
        release_func = get_release_func(ae_lib)

        anchor_arr = ctypes.POINTER(ctypes.c_uint)()
        if file_path is not None:
            len_anchor_arr = ae_chunking_func(file_path.encode(), anchor_arr, self.window_size)
        else:
            len_anchor_arr = ae_chunking_func(file_bytes, len(file_bytes), anchor_arr, self.window_size)

        chunk_list = []
        last_anchor = 0
        if file_bytes is None and file_path is not None:
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
        for i in range(len_anchor_arr):
            chunk_list.append(file_bytes[last_anchor:anchor_arr[i]])
            last_anchor = anchor_arr[i]
        release_func(anchor_arr)
        return chunk_list

    def get_info(self):
        info = "AsymmetricExtremum_w_{}".format(self.__dict__['window_size'])
        return info

    # def bytes_ae(self, byte_seq, window_size):
    #     bytes_len = len(byte_seq)
    #     chunk_bytes_list = []
    #     byte_idx = 0
    #     byte_arr = bytearray()
    #     # this while for all file content
    #     while byte_idx < bytes_len:
    #         # ae chunking algorithm section
    #         max_value = byte_seq[byte_idx]
    #         max_position = byte_idx
    #         byte_arr.append(byte_seq[byte_idx])
    #         byte_idx += 1
    #         while byte_idx < bytes_len:
    #             if byte_seq[byte_idx] <= max_value:
    #                 if byte_idx == max_position + window_size:
    #                     content_bytes = bytes(byte_arr)
    #                     chunk_bytes_list.append(content_bytes)
    #                     byte_arr = bytearray()
    #                     byte_idx += 1
    #                     break
    #             else:
    #                 max_value = byte_seq[byte_idx]
    #                 max_position = byte_idx
    #             byte_arr.append(byte_seq[byte_idx])
    #             byte_idx += 1
    #     if len(byte_arr):
    #         content_bytes = bytes(byte_arr)
    #         chunk_bytes_list.append(content_bytes)
    #     return chunk_bytes_list