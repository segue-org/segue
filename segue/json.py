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
            return flask.jsoned(dict(items=result)), status
        else:
            return flask.jsonify(dict(resource=result)), status
    return wrapper


class JSONEncoder(flask.json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, JsonSerializer):
            return obj.to_json()
        return super(JSONEncoder, self).default(obj)

class JsonSerializer(object):
    def to_json(self):
        raise NotImplemented()

class PropertyJsonSerializer(JsonSerializer):
    __json_public__ = None
    __json_hidden__ = None
    __json_modifiers__ = None

    def get_field_names(self):
        return NotImplemented()

    def to_json(self):
        field_names = self.get_field_names()

        public = self.__json_public__ or field_names
        hidden = self.__json_hidden__ or []
        modifiers = self.__json_modifiers__ or dict()

        rv = dict()
        for key in public:
            rv[key] = getattr(self, key)
        for key, modifier in modifiers.items():
            value = getattr(self, key)
            rv[key] = modifier(value, self)
        for key in hidden:
            rv.pop(key, None)
        for key in rv.keys():
            if rv.get(key) == None:
                rv.pop(key)
        return rv

class SQLAlchemyJsonSerializer(PropertyJsonSerializer):
    def get_field_names(self):
        for p in self.__mapper__.iterate_properties:
            yield p.key

