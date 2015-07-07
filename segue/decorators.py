from werkzeug.wrappers import Response
from functools import wraps
import flask

from segue.errors import NotAuthorized
from segue.core import jwt_required, logger

def admin_only(fn):
    @wraps(fn)
    def wrapped(instance, *args, **kw):
        if instance.current_user.role != 'admin':
            logger.info("denied access to admin-only endpoint: %s", instance.current_user.__dict__)
            raise NotAuthorized()
        return fn(instance, *args, **kw)
    return wrapped

def cashier_only(fn):
    @wraps(fn)
    def wrapped(instance, *args, **kw):
        if instance.current_user.role not in ('admin', 'cashier'):
            logger.info("denied access to cashier-only endpoint: %s", instance.current_user.__dict__)
            raise NotAuthorized()
        return fn(instance, *args, **kw)
    return wrapped

def frontdesk_only(fn):
    @wraps(fn)
    def wrapped(instance, *args, **kw):
        if instance.current_user.role not in ('admin', 'frontdesk', 'cashier'):
            logger.info("denied access to frontdesk-only endpoint: %s", instance.current_user.__dict__)
            raise NotAuthorized()
        return fn(instance, *args, **kw)
    return wrapped

def jwt_only(fn):
    @wraps(fn)
    def wrapped(instance, *args, **kw):
        return jwt_required()(fn)(instance, *args, **kw)
    return wrapped

def accepts_html(f):
    @wraps(f)
    def wrapper(*args, **kw):
        best = flask.request.accept_mimetypes.best_match(['application/json', 'text/html'])
        kw['wants_html'] = best == 'text/html'
        return f(*args, **kw)
    return wrapper

def jsoned(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        status = 200
        result = f(*args, **kwargs)
        if isinstance(result, Response):
            return result
        if isinstance(result, tuple):
            result, status = result
        if isinstance(result, list):
            return flask.jsonify(dict(count=len(result),items=result)), status
        elif isinstance(result, dict):
            return flask.jsonify(dict(**result)), status
        elif hasattr(result, 'to_json'):
            return flask.jsonify(dict(resource=result.to_json())), status
        else:
            return flask.jsonify(dict(resource=result)), status
    return wrapper
