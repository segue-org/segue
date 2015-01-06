import re
from json import JsonSerializer

class SegueError(JsonSerializer, Exception):
    pass

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
