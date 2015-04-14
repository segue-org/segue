import flask
from flask import request
from flask.ext.jwt import current_user, verify_jwt, JWTError

from ..core import jwt_required
from ..json import jsoned, accepts_html, JsonFor

import schema

from models import Caravan, CaravanInvite
from services import CaravanService, CaravanInviteService

class CaravanController(object):
    def __init__(self, service=None):
        self.service = service or CaravanService()
        self.current_user = current_user

    @jwt_required()
    @jsoned
    def create(self):
        data = request.get_json()
        return self.service.create(data, self.current_user), 201

    @jwt_required()
    @jsoned
    def get_one(self, caravan_id=None):
        if caravan_id:
            result = self.service.get_one(caravan_id, self.current_user) or flask.abort(404)
        else:
            if request.args.get('owner_id') is not None:
                owner_id = request.args.get('owner_id')
            else:
                owner_id = self.current_user.id
            result = self.service.get_by_owner(owner_id, self.current_user)
        return result, 200

    @jsoned
    def schema(self, name):
        return schema.whitelist[name], 200

class CaravanInviteController(object):
    def __init__(self, service=None):
        self.service = service or CaravanInviteService()
        self.current_user = current_user

    @jwt_required()
    @jsoned
    def list(self, caravan_id):
        result = self.service.list(caravan_id, by=self.current_user)
        return JsonFor(result).using('ShortCaravanInviteJsonSerializer'), 200

    @jsoned
    @accepts_html
    def get_by_hash(self, caravan_id, hash_code, wants_html=False):
        invite = self.service.get_by_hash(hash_code) or flask.abort(404)
        if wants_html:
            path = '/#/caravan/{}/invite/{}/answer'.format(caravan_id, hash_code)
            return flask.redirect(config.FRONTEND_URL + path)
        else:
            return invite, 200

    @jwt_required()
    @jsoned
    def create(self, caravan_id):
        data = request.get_json()
        result = self.service.create(caravan_id, data, by=self.current_user)
        return result, 200

    @jsoned
    def accept(self, caravan_id, hash_code):
        try:
            verify_jwt()
        except JWTError:
            pass

        result = self.service.answer(hash_code, accepted=True, by=self.current_user) or flask.abort(404)
        return result, 200

    @jsoned
    def decline(self, caravan_id, hash_code):
        result = self.service.answer(hash_code, accepted=False) or flask.abort(404)
        return result, 200

    @jsoned
    def register(self, caravan_id, hash_code):
        data = request.get_json()
        result = self.service.register(hash_code, data) or flask.abort(404)
        return result, 200
