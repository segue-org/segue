import jsonschema

from errors import SegueValidationError

class Factory(object):
    @classmethod
    def from_json(cls, data, schema):
        validator = jsonschema.Draft4Validator(schema)
        errors = list(validator.iter_errors(data))
        if errors:
            raise SegueValidationError(errors)
        return cls.model(**data)


