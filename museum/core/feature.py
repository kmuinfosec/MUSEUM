class Base:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def process(self, file_path=None, file_bytes=None):
        pass

    def get_info(self):
        pass