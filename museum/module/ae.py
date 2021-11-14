from museum.core.feature import Base
import os
import ctypes
import platform


class AsymmetricExtremum(Base):
    def __int__(self, **kwargs):
        super().__init__(**kwargs)
        if 'window_size' not in self.__dict__:
            msg = "Parameter 'window_size' must be passed"
            raise Exception(msg)
        self.window_size = self.__dict__['window_size']

    def process(self, file_path, file_bytes=None):
        if file_bytes is None:
            if not os.path.isfile(file_path):
                error_msg = "{} does not exist".format(file_path)
                raise FileNotFoundError(error_msg)
        ae_dll = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ae_{}.dll'.format(platform.architecture()[0])))
        ae_chunking = ae_dll.ae_chunking
        ae_chunking.argtypes = (
            ctypes.c_char_p, ctypes.c_ulong,
            ctypes.POINTER(ctypes.POINTER(ctypes.c_uint)), ctypes.c_char_p, ctypes.c_uint
        )
        ae_chunking.restype = ctypes.c_uint
        release = ae_dll.release
        release.argtypes = [ctypes.POINTER(ctypes.c_uint)]
        release.restype = None
        if file_bytes is None:
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
        anchor_arr = ctypes.POINTER(ctypes.c_uint)()
        len_anchor_arr = ae_chunking(file_bytes, len(file_bytes), anchor_arr, file_path.encode(), self.window_size)

        last_anchor = 0
        chunk_list = []
        for i in range(len_anchor_arr):
            chunk_list.append(file_bytes[last_anchor:anchor_arr[i]])
            last_anchor = anchor_arr[i]
        release(anchor_arr)
        return chunk_list
        # chunk_list = self.bytes_ae(file_bytes, self.__dict__['window_size'])
        # return list(set(chunk_list))

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