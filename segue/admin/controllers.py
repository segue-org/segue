import inspect

from segue.decorators import admin_only, jwt_only
from flask.ext.jwt import current_user

class BaseAdminController(object):
    def __init__(self):
        self.current_user = current_user
