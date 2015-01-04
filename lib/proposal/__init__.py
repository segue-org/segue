import flask

from ..core import db
from ..helpers import jsoned
from models import Proposal

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
    def get_one(self, proposal_id):
        return self.service.get_one(proposal_id), 200
