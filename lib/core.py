import flask_sqlalchemy
import jsonschema, jsonschema.exceptions
from helpers import JsonSerializer

db = flask_sqlalchemy.SQLAlchemy()

class SegueError(JsonSerializer, Exception): pass

class SegueValidationError(SegueError):
    def __init__(self, errors):
        messages = [ e.message for e in errors ]
        super(SegueValidationError, self).__init__(*messages)

class Factory(object):
    @classmethod
    def from_json(cls, data, schema):
        validator = jsonschema.Draft4Validator(schema)
        errors = list(validator.iter_errors(data))
        if errors:
            raise SegueValidationError(errors)
        return cls.model(**data)

def log(*args):
    with open("/tmp/segue.log", "a+") as logfile:
        print >> logfile, args
