from ..core import db
from ..errors import NotAuthorized

import schema
from factories import ProposalFactory, InviteFactory
from models    import Proposal

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

    def invite(self, proposal_id, data, by=None):
        proposal = self.get_one(proposal_id)
        if not self._check_ownership(proposal, by): raise NotAuthorized

        invite = InviteFactory.from_json(data, schema.new_invite)
        invite.proposal = proposal

        db.session.add(invite)
        db.session.commit()

        return invite

    def _check_ownership(self, proposal, alleged):
        return proposal and alleged and proposal.owner_id == alleged.id


