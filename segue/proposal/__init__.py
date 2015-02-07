import sys
import flask

from flask import request
from flask.ext.jwt import current_user

from ..core import db, jwt_required
from ..json import jsoned
from ..factory import Factory
from ..errors import NotAuthorized

import schema
from models import Proposal

QUERY_WHITELIST = ('owner_id',)

class ProposalFactory(Factory):
    model = Proposal

    UPDATE_WHITELIST = schema.edit_proposal["properties"].keys()

    @classmethod
    def clean_for_update(self, data):
        return { c:v for c,v in data.items() if c in ProposalFactory.UPDATE_WHITELIST }


class ProposalService(object):
    def __init__(self, db_impl=None):
        self.db = db_impl or db

    def create(self, data, owner):
        proposal = ProposalFactory.from_json(data, schema.new_proposal)
        proposal.owner = owner
        db.session.add(proposal)
        db.session.commit()
        return proposal

    def get_one(self, proposal_id):
        return Proposal.query.get(proposal_id)

    def query(self, **kw):
        return Proposal.query.filter_by(**kw).all()

    def modify(self, proposal_id, data, by=None):
        proposal = self.get_one(proposal_id)
        if not self._check_ownership(proposal, by): raise NotAuthorized

        for name, value in ProposalFactory.clean_for_update(data).items():
            setattr(proposal, name, value)
        db.session.add(proposal)
        db.session.commit()
        return proposal

    def _check_ownership(self, proposal, alleged):
        return proposal and alleged and proposal.owner_id == alleged.id



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

    @jwt_required
    @jsoned
    def invite(self, proposal_id):
        if not self.service.check_ownership(proposal_id, self.current_user):
            flask.abort(403)
        data = request.get_json()
        result = self.service.invite(proposal_id, data)
        return result, 200

    @jsoned
    def invite_answer(self, proposal_id, invite_id):
        data = request.get_json()
        self.service.invite_answer(proposal_id, invite_id, data)
        return {}, 200

    @jsoned
    def get_one(self, proposal_id):
        result = self.service.get_one(proposal_id) or flask.abort(404)
        return result, 200

    @jsoned
    def list(self):
        parms = { c: request.args.get(c) for c in QUERY_WHITELIST if c in request.args }

        result = self.service.query(**parms)
        return result, 200

    @jsoned
    def schema(self, name):
        return schema.whitelist[name], 200


