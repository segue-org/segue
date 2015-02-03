import sys
import flask

from flask import request
from flask.ext.jwt import current_user

from ..core import db, jwt_required
from ..json import jsoned
from ..factory import Factory

import schema
from models import Proposal

QUERY_WHITELIST = ('owner_id',)

class ProposalFactory(Factory):
    model = Proposal

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


class ProposalController(object):
    def __init__(self, service=None):
        self.service = service or ProposalService()
        self.current_user = current_user

    @jwt_required()
    @jsoned
    def create(self):
        data = request.get_json()
        return self.service.create(data, self.current_user), 201

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
