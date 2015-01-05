import sys
import jsonschema, jsonschema.exceptions
import flask

from flask import request

from ..core import db, log
from ..helpers import jsoned

from models import Proposal
from schema import new_proposal_schema

class ProposalService(object):
    def __init__(self, db_impl=None):
        self.db = db_impl or db

    def create(self, proposal):
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
        try:
            data = request.get_json()
            jsonschema.validate(data, new_proposal_schema)
            self.service.create(data)
            return data, 201
        except jsonschema.exceptions.ValidationError, e:
            print e.message
            return e.context.iter_errors, 422

    @jsoned
    def get_one(self, proposal_id):
        result = self.service.get_one(proposal_id) or flask.abort(404)
        return result, 200
