import flask
from flask import request
from flask.ext.jwt import current_user, verify_jwt, JWTError

from ..core import jwt_required, config
from ..json import jsoned, accepts_html, JsonFor

import schema

from models import Corporate
from services import CorporateService, CorporateAccountService

class CorporateController(object):
    def __init__(self, service=None, employee_service=None):
        self.service = service or CorporateService()
        self.employee_service = employee_service or CorporateAccountService()
        self.current_user = current_user

    @jwt_required()
    @jsoned
    def list(self, corporate_id):
        result = self.service.list(corporate_id, by=self.current_user)
        return JsonFor(result).using('ShortCorporateJsonSerializer'), 200

    @jwt_required()
    @jsoned
    def create(self):
        data = request.get_json()
        return self.service.create(data, self.current_user), 201

    @jwt_required()
    @jsoned
    def modify(self, corporate_id):
        data = request.get_json()
        result = self.service.modify(corporate_id, data, by=self.current_user) or flask.abort(404)
        return result, 200

    @jwt_required()
    @jsoned
    def get_one(self, corporate_id=None):
        if corporate_id:
            result = self.service.get_one(corporate_id, self.current_user) or flask.abort(404)
        else:
            owner_id = int(request.args.get('owner_id', self.current_user.id))
            result = self.service.get_by_owner(owner_id, self.current_user)
        return result, 200

    @jwt_required()
    @jsoned
    def add_people(self, corporate_id):
        data = request.get_json()
        return self.employee_service.create(corporate_id, data, self.current_user), 201

    @jsoned
    def schema(self, name):
        return schema.whitelist[name], 200
