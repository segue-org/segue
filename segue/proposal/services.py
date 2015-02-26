import random

from ..core import db
from ..errors import NotAuthorized
from ..mailer import MailerService

import schema
from factories import ProposalFactory, InviteFactory
from models    import Proposal, ProposalInvite, Track
from ..account import AccountService

class Hasher(object):
    def __init__(self, length=32):
        self.length = length

    def generate(self):
        value = random.getrandbits(self.length * 4)
        return "{0:0{1}X}".format(value, self.length)

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
        if not self.check_ownership(proposal, by): raise NotAuthorized

        for name, value in ProposalFactory.clean_for_update(data).items():
            setattr(proposal, name, value)
        db.session.add(proposal)
        db.session.commit()
        return proposal

    def check_ownership(self, proposal, alleged):
        if isinstance(proposal, int): proposal = self.get_one(proposal)
        return proposal and alleged and proposal.owner_id == alleged.id

    def list_tracks(self):
        return Track.query.all()

class InviteService(object):
    def __init__(self, proposals=None, hasher=None, accounts = None, mailer=None):
        self.proposals = proposals or ProposalService()
        self.hasher    = hasher    or Hasher()
        self.mailer    = mailer    or MailerService()
        self.accounts  = accounts  or AccountService()

    def list(self, proposal_id, by=None):
        proposal = self.proposals.get_one(proposal_id)
        if not self.proposals.check_ownership(proposal, by): raise NotAuthorized
        return proposal.invites

    def get_one(self, invite_id):
        return ProposalInvite.query.get(invite_id)

    def get_by_hash(self, invite_hash):
        candidates = ProposalInvite.query.filter_by(hash=invite_hash).all()
        return candidates[0] if len(candidates) else None

    def create(self, proposal_id, data, by=None):
        proposal = self.proposals.get_one(proposal_id)
        if not self.proposals.check_ownership(proposal, by): raise NotAuthorized

        invite = InviteFactory.from_json(data, schema.new_invite)
        invite.proposal = proposal
        invite.hash     = self.hasher.generate()

        db.session.add(invite)
        db.session.commit()

        self.mailer.proposal_invite(invite)

        return invite

    def answer(self, hash, accepted=True, by=None):
        invite = self.get_by_hash(hash)
        if not invite:
            return None
        if self.accounts.is_email_registered(invite.recipient):
            if not by or by.email != invite.recipient:
                raise NotAuthorized

        invite.status = 'accepted' if accepted else 'declined'
        db.session.add(invite)
        db.session.commit()
        return invite

    def register(self, hash, account_data):
        invite = self.get_by_hash(hash)
        if not invite:
            return None
        if invite.recipient != account_data['email']:
            return NotAuthorized

        return self.accounts.create(account_data)


