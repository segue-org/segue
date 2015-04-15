from functools import wraps

from flask import request
from flask.ext.jwt import current_user

from ..errors import NotAuthorized
from ..core import jwt_required, config, logger
from ..json import jsoned

from segue.account import AccountService

def admin_only(fn):
    @wraps(fn)
    def wrapped(instance, *args, **kw):
        logger.info(instance.current_user.__dict__)
        if instance.current_user.role != 'admin':
            raise NotAuthorized()
        return fn(instance, *args, **kw)
    return wrapped

class AccountDetailResponse(object):
    def __init__(self, list_or_entity):
        if isinstance(list_or_entity, list):
            return [ Account(e) for e in list_or_entity ]
        self.bla = 'bla'

class AdminController(object):
    def __init__(self, accounts=None):
        self.accounts     = accounts or AccountService()
        self.current_user = current_user

    @jwt_required()
    @admin_only
    @jsoned
    def lookup(self):
        criteria = request.args.get('q')
        result = self.accounts.lookup(criteria)
        return AccountDetailResponse(result), 200
