class Base:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def process(self, file_path):
        pass

    def get_info(self):
        pass