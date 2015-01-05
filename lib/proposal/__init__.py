import sys

import flask
from flask import request

from ..core import db, log
from ..helpers import jsoned
from models import Proposal
from forms import NewProposalForm

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

    def create(self):
        form = NewProposalForm(request.get_json())
        if form.validate():
            return '', 201
        else:
            return form, 422

    @jsoned
    def get_one(self, proposal_id):
        result = self.service.get_one(proposal_id) or flask.abort(404)
        return result, 200
