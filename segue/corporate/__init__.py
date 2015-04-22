import flask
from flask import request
from flask.ext.jwt import current_user, verify_jwt, JWTError

from ..core import jwt_required, config
from ..json import jsoned, accepts_html, JsonFor

import schema

from models import Corporate, CorporateInvite
from services import CorporateService, CorporateInviteService

class CorporateController(object):
    def __init__(self, service=None):
        self.service = service or CorporateService()
        self.current_user = current_user

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

    @jsoned
    def schema(self, name):
        return schema.whitelist[name], 200

class CorporateInviteController(object):
    def __init__(self, service=None):
        self.service = service or CorporateInviteService()
        self.current_user = current_user

    @jwt_required()
    @jsoned
    def list(self, corporate_id):
        result = self.service.list(corporate_id, by=self.current_user)
        return JsonFor(result).using('ShortCorporateInviteJsonSerializer'), 200

    @jsoned
    @accepts_html
    def get_by_hash(self, corporate_id, hash_code, wants_html=False):
        invite = self.service.get_by_hash(hash_code) or flask.abort(404)
        if wants_html:
            path = '/#/corporate/{}/invite/{}/answer'.format(corporate_id, hash_code)
            return flask.redirect(config.FRONTEND_URL + path)
        else:
            return invite, 200

    @jwt_required()
    @jsoned
    def create(self, corporate_id):
        data = request.get_json()
        result = self.service.create(corporate_id, data, by=self.current_user)
        return result, 200

    @jsoned
    def accept(self, corporate_id, hash_code):
        try:
            verify_jwt()
        except JWTError:
            pass

        result = self.service.answer(hash_code, accepted=True, by=self.current_user) or flask.abort(404)
        return result, 200

    @jsoned
    def decline(self, corporate_id, hash_code):
        result = self.service.answer(hash_code, accepted=False) or flask.abort(404)
        return result, 200

    @jsoned
    def register(self, corporate_id, hash_code):
        data = request.get_json()
        result = self.service.register(hash_code, data) or flask.abort(404)
        return result, 200
