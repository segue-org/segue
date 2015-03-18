import flask

from flask import request
from flask.ext.jwt import current_user, verify_jwt, JWTError

from ..core import jwt_required, config
from ..json import jsoned, accepts_html, JsonFor

import schema
from factories import ProposalFactory
from services  import ProposalService, InviteService

class ProposalController(object):
    def __init__(self, service=None):
        self.service = service or ProposalService()
        self.current_user = current_user

    @jwt_required()
    @jsoned
    def create(self):
        data = request.get_json()
        return self.service.create(data, self.current_user), 201

    @jwt_required()
    @jsoned
    def modify(self, proposal_id):
        data = request.get_json()
        result = self.service.modify(proposal_id, data, by=self.current_user) or flask.abort(404)
        return result, 200

    @jsoned
    def get_one(self, proposal_id):
        result = self.service.get_one(proposal_id) or flask.abort(404)
        return result, 200

    @jsoned
    @jwt_required()
    def list(self):
        parms = { c: request.args.get(c) for c in ProposalFactory.QUERY_WHITELIST if c in request.args }
        result = self.service.query(as_user=self.current_user, **parms)
        return JsonFor(result).using('ShortChildProposalJsonSerializer'), 200

    @jsoned
    def schema(self, name):
        return schema.whitelist[name], 200

    @jsoned
    def list_tracks(self):
        return self.service.list_tracks()


class ProposalInviteController(object):
    def __init__(self, service=None):
        self.service      = service   or InviteService()
        self.current_user = current_user

    @jwt_required()
    @jsoned
    def list(self, proposal_id):
        result = self.service.list(proposal_id, by=self.current_user)
        return JsonFor(result).using('ShortInviteJsonSerializer'), 200

    @jsoned
    @accepts_html
    def get_by_hash(self, proposal_id, hash_code, wants_html=False):
        invite = self.service.get_by_hash(hash_code) or flask.abort(404)
        if wants_html:
            path = '/#/proposal/{}/invite/{}/answer'.format(proposal_id, hash_code)
            return flask.redirect(config.FRONTEND_URL + path)
        else:
            return invite, 200

    @jwt_required()
    @jsoned
    def create(self, proposal_id):
        data = request.get_json()
        result = self.service.create(proposal_id, data, by=self.current_user)
        return result, 200

    @jsoned
    def decline(self, proposal_id, hash_code):
        result = self.service.answer(hash_code, accepted=False) or flask.abort(404)
        return result, 200

    @jsoned
    def accept(self, proposal_id, hash_code):
        try:
            verify_jwt()
        except JWTError:
            pass

        result = self.service.answer(hash_code, accepted=True, by=self.current_user) or flask.abort(404)
        return result, 200

    @jsoned
    def register(self, proposal_id, hash_code):
        data = request.get_json()
        result = self.service.register(hash_code, data) or flask.abort(404)
        return result, 200

