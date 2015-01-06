import sys
import flask

from flask import request

from ..core import db
from ..json import jsoned
from ..factory import Factory
from ..errors import SegueValidationError

from models import Proposal
from schema import new_proposal_schema

class ProposalFactory(Factory):
    model = Proposal

class ProposalService(object):
    def __init__(self, db_impl=None):
        self.db = db_impl or db

    def create(self, data):
        proposal = ProposalFactory.from_json(data, new_proposal_schema)
        db.session.add(proposal)
        db.session.commit()
        return proposal

    def get_one(self, proposal_id):
        return Proposal.query.get(proposal_id)


class ProposalController(object):
    def __init__(self, service=None):
        self.service = service or ProposalService()

    @jsoned
    def create(self):
        data = request.get_json()
        return self.service.create(data), 201

    @jsoned
    def get_one(self, proposal_id):
        result = self.service.get_one(proposal_id) or flask.abort(404)
        return result, 200
