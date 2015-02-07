import sys
import flask

from flask import request
from flask.ext.jwt import current_user

from ..core import jwt_required
from ..json import jsoned

import schema
from factories import ProposalFactory
from services  import ProposalService

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
    def list(self):
        parms = { c: request.args.get(c) for c in ProposalFactory.QUERY_WHITELIST if c in request.args }

        result = self.service.query(**parms)
        return result, 200

    @jsoned
    def schema(self, name):
        return schema.whitelist[name], 200

    @jwt_required()
    @jsoned
    def invite(self, proposal_id):
        data = request.get_json()
        result = self.service.invite(proposal_id, data, by=self.current_user)
        return result, 200

    @jsoned
    def invite_answer(self, proposal_id, invite_id):
        data = request.get_json()
        self.service.invite_answer(proposal_id, invite_id, data)
        return {}, 200




