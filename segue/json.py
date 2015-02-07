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
        elif hasattr(result, 'to_json'):
            return flask.jsonify(dict(resource=result.to_json())), status
        else:
            return flask.jsonify(dict(resource=result)), status
    return wrapper


class JSONEncoder(flask.json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, JsonSerializable):
            return obj.serialize()
        return super(JSONEncoder, self).default(obj)

class JsonSerializable(object):
    _serializers = [ ]

    def serialize(self, **kw):
        candidates = []
        candidates.extend(self._serializers)
        candidates.append(JsonSerializer)
        serializer = candidates[0]()
        return serializer.emit_json_for(self, **kw)

    def to_json(self, **kw):
        return self.serialize(**kw)

class JsonSerializer(object):
    def hide_child(self, child):
        return False;

    def serialize_child(self, child):
        return False

    def emit_json_for(self, target, **kw):
        if hasattr(target, 'to_json'):
            return target.to_json()
        return target

class PropertyJsonSerializer(JsonSerializer):
    def get_field_names(self, target):
        raise NotImplementedError()

    def emit_json_for(self, target, all_fields=False, **overrides):
        # WORST CODE EVER
        result = {}
        for key, serializer in self.get_field_names(target):
            value          = getattr(target, key, None)
            override       = overrides.get(key, None)
            hide_field     = self.hide_child(key)
            recurse_with   = self.serialize_child(key)
            is_list        = isinstance(value, list)
            is_nested_list = is_list and any([ isinstance(x, JsonSerializable) for x in value ])
            is_nested      = is_nested_list or isinstance(value, JsonSerializable)
            available      = value[0]._serializers if is_nested_list else getattr(value, '_serializers', [])

            selected   = override or recurse_with or 'JsonSerializer'
            serializer = JsonSerializer()
            for cls in available:
                if cls.__name__ == selected:
                    serializer = cls()
                    break
            if is_nested_list:
                if not recurse_with: continue
                result[key] = [ serializer.emit_json_for(item, **overrides) for item in value ]
            elif is_nested:
                if not recurse_with: continue
                result[key] = serializer.emit_json_for(value, **overrides)
            elif value and not hide_field:
                result[key] = serializer.emit_json_for(value, **overrides)

        return result

class SQLAlchemyJsonSerializer(PropertyJsonSerializer):
    def get_field_names(self, target):
        for p in target.__mapper__.iterate_properties:
            if p.key.endswith("_id"): continue
            yield [ p.key, None ]
