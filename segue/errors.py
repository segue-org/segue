import re
from json import JsonSerializer

class SegueError(JsonSerializer, Exception):
    code = 400

    def __init__(self):
        self.code   = self.__class__.code
        super(SegueError, self).__init__()

class SegueValidationError(SegueError):
    def __init__(self, errors):
        self.errors = errors
        super(SegueValidationError, self).__init__()

    def to_json(self):
        result = {}
        for error in self.errors:
            message = re.sub("u('.*?')",r"\1",error.message)
            path = ".".join(error.schema_path)
            result[path] = message
        return result

class InvalidLogin(SegueError):
    code = 400

    def to_json(self):
        return [ 'bad login' ]

