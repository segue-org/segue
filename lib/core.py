import flask_sqlalchemy
from helpers import JsonSerializer

db = flask_sqlalchemy.SQLAlchemy()

class SegueError(JsonSerializer, Exception): pass

class SegueValidationError(SegueError):
    def __init__(self, errors):
        messages = [ e.message for e in errors ]
        super(SegueValidationError, self).__init__(*messages)

def log(*args):
    with open("/tmp/segue.log", "a+") as logfile:
        print >> logfile, args
