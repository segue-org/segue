from flask import request
from flask.ext.jwt import current_user

from ..core import jwt_required
from ..json import jsoned

import schema

from models import Caravan, CaravanInvite
from services import CaravanService

class CaravanController(object):
    def __init__(self, service=None):
        self.service = service or CaravanService()
        self.current_user = current_user

    @jwt_required()
    @jsoned
    def create(self):
        data = request.get_json()
        return self.service.create(data, self.current_user), 201

    @jsoned
    def schema(self, name):
        return schema.whitelist[name], 200

