class AlreadyExistError(Exception):
    def __init__(self, message):
        super(AlreadyExistError, self).__init__(message)


class NotExistError(Exception):
    def __init__(self, message):
        super(NotExistError, self).__init__(message)


class NotDefinedError(Exception):
    def __init__(self, message):
        super(NotDefinedError, self).__init__(message)
