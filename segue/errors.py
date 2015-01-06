from helpers import JsonSerializer

class SegueError(JsonSerializer, Exception):
    pass

class SegueValidationError(SegueError):
    def __init__(self, errors):
        messages = [ e.message for e in errors ]
        super(SegueValidationError, self).__init__(*messages)


