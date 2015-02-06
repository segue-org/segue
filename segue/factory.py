import jsonschema

from errors import SegueValidationError

class Factory(object):
    @classmethod
    def clean_for_insert(cls, data):
        return data;

    @classmethod
    def from_json(cls, data, schema):
        cleaned_data = cls.clean_for_insert(data)
        validator = jsonschema.Draft4Validator(schema)
        errors = list(validator.iter_errors(cleaned_data))
        if errors:
            raise SegueValidationError(errors)
        return cls.model(**cleaned_data)


