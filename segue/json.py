from functools import wraps
import flask

def jsoned(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        status = 200
        result = f(*args, **kwargs)
        if isinstance(result, tuple):
            result, status = result
        if isinstance(result, list):
            return flask.jsonify(dict(items=result)), status
        elif isinstance(result, dict):
            return flask.jsonify(dict(**result)), status
        else:
            return flask.jsonify(dict(resource=result)), status
    return wrapper


class JSONEncoder(flask.json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, JsonSerializable):
            return obj.serialize()
        return super(JSONEncoder, self).default(obj)

class JsonSerializer(object):
    def __init__(self, target):
        self.target = target

    def override_child(self, field_name, replacement):
        field = getattr(self.target, field_name)
        if field is not None:
            field._serializer = replacement

    def override_children(self):
        pass

    def to_json(self, **kw):
        return self.target.to_json(**kw)

class PropertyJsonSerializer(JsonSerializer):
    __json_public__ = None
    __json_hidden__ = None

    def get_field_names(self):
        return NotImplemented()

    def override_field_serializer(self):
        pass

    def to_json(self, **kw):
        field_names = self.get_field_names()

        if kw.pop('all_fields',False):
            public = field_names
            hidden = []
        else:
            public = self.__json_public__ or field_names
            hidden = self.__json_hidden__ or []

        rv = dict()
        for key in public:
            rv[key] = getattr(self.target, key)
        for key in hidden:
            rv.pop(key, None)
        for key in rv.keys():
            if rv.get(key) == None:
                rv.pop(key)
        return rv

class SQLAlchemyJsonSerializer(PropertyJsonSerializer):
    def get_field_names(self):
        for p in self.target.__mapper__.iterate_properties:
            yield p.key

class JsonSerializable(object):
    _serializer = JsonSerializer

    def serialize(self, **kw):
        serializer = self._serializer(self)
        serializer.override_children()
        return serializer.to_json(**kw)

    def to_json(self, **kw):
        return self.serialize(**kw)


