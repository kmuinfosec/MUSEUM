from museum.core.feature import Base
import os


class AsymmetricExtremum(Base):
    def __int__(self, **kwargs):
        super().__init__(**kwargs)

    def process(self, file_path):
        if 'window_size' not in self.__dict__:
            msg = "Parameter 'window_size' must be passed"
            raise Exception(msg)
        if not os.path.isfile(file_path):
            error_msg = "{} does not exist".format(file_path)
            raise Exception(error_msg)
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        chunk_list = self.bytes_ae(file_bytes, self.__dict__['window_size'])
        return list(set(chunk_list))

    def get_info(self):
        info = "AsymmetricExtremum(w={})".format(self.__dict__['window_size'])
        return info

    def bytes_ae(self, byte_seq, window_size):
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
