from datetime import datetime
import random
from sqlalchemy import and_, or_

from ..core import db, config
from ..errors import NotAuthorized, DeadlineReached
from ..mailer import MailerService
from ..hasher import Hasher
from ..filters import FilterStrategies

from ..account import AccountService

import schema
from factories import ProposalFactory, InviteFactory
from models    import Proposal, ProposalInvite, Track
from filters import ProposalFilterStrategies

class CallForPapersDeadline(object):
    def __init__(self, override_config=None):
        self.config = override_config or config

    def is_past(self):
        return datetime.now() > self.config.CALL_FOR_PAPERS_DEADLINE

    def enforce(self):
        if self.is_past():
            raise DeadlineReached()

class ProposalService(object):
    def __init__(self, db_impl=None, deadline=None):
        self.db = db_impl or db
        self.filter_strategies = ProposalFilterStrategies()
        self.deadline = deadline or CallForPapersDeadline()

    def cfp_state(self):
        return 'closed' if self.deadline.is_past() else 'open'

    def create(self, data, owner):
        self.deadline.enforce()

        proposal = ProposalFactory.from_json(data, schema.new_proposal)
        proposal.owner = owner
        db.session.add(proposal)
        db.session.commit()
        return proposal

    def get_one(self, proposal_id):
        return Proposal.query.get(proposal_id)

    def query(self, **kw):
        filter_list = self.filter_strategies.given(**kw)
        return Proposal.query.filter(*filter_list).all()

    def modify(self, proposal_id, data, by=None):
        self.deadline.enforce()

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

    def by_coauthor(self, coauthor_id):
        return Proposal.query.filter(Proposal.invites.any(recipient=coauthor_id)).all()

class InviteService(object):
    def __init__(self, proposals=None, hasher=None, accounts = None, mailer=None, deadline=None):
        self.proposals = proposals or ProposalService()
        self.hasher    = hasher    or Hasher()
        self.mailer    = mailer    or MailerService()
        self.accounts  = accounts  or AccountService()
        self.deadline  = deadline  or CallForPapersDeadline()

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
        self.deadline.enforce()

        proposal = self.proposals.get_one(proposal_id)
        if not self.proposals.check_ownership(proposal, by): raise NotAuthorized

        invite = InviteFactory.from_json(data, schema.new_invite)
        invite.proposal = proposal
        invite.hash     = self.hasher.generate()

        db.session.add(invite)
        db.session.commit()

        self.mailer.proposal_invite(invite)

        return invite

    def answer(self, hash_code, accepted=True, by=None):
        self.deadline.enforce()

        invite = self.get_by_hash(hash_code)
        if not invite:
            return None
        if self.accounts.is_email_registered(invite.recipient):
            if not by or by.email != invite.recipient:
                raise NotAuthorized

        invite.status = 'accepted' if accepted else 'declined'
        db.session.add(invite)
        db.session.commit()
        return invite

    def register(self, hash_code, account_data):
        self.deadline.enforce()
        invite = self.get_by_hash(hash_code)
        if not invite:
            return None
        if invite.recipient != account_data['email']:
            raise NotAuthorized

        return self.accounts.create(account_data)


