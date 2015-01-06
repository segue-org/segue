import re
from json import JsonSerializer

class SegueError(JsonSerializer, Exception):
    pass

class SegueValidationError(SegueError):
    __json__public__ = [ 'errors']
    def __init__(self, errors):
        self.errors = map(self._build_error, errors)
        super(SegueValidationError, self).__init__()

    def to_json(self):
        return self.errors

    def _build_error(self, error):
        message = re.sub("u('.*?')",r"\1",error.message)
        path = ".".join(error.schema_path)
        return dict(message=message, path=path)




