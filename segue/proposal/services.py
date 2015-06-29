from datetime import datetime
import random
from sqlalchemy import and_, or_

from ..core import db, config
from ..errors import NotAuthorized
from ..hasher import Hasher
from ..filters import FilterStrategies

from segue.mailer import MailerService
from segue.account.services import AccountService

import schema
from errors import DeadlineReached, NoSuchProposal, SegueError
from factories import ProposalFactory, InviteFactory
from models import ProposalTag, Proposal, ProposalInvite, Track, NonSelectionNotice, ProponentProduct
from filters import ProposalFilterStrategies

class CallForPapersDeadline(object):
    def __init__(self, override_config=None):
        self.config = override_config or config

    def is_past(self):
        return datetime.now() > self.config.CALL_FOR_PAPERS_DEADLINE

    def enforce(self):
        if self.is_past():
            raise DeadlineReached()

class NonSelectionService(object):
    def __init__(self, hasher=None, mailer=None):
        self.hasher = hasher or Hasher()
        self.mailer = mailer or MailerService()

    def create_and_send(self, account):
        existing = NonSelectionNotice.query.filter(NonSelectionNotice.account==account).first()
        if existing: return existing

        notice = NonSelectionNotice(account=account)
        notice.hash = self.hasher.generate()
        db.session.add(notice)
        db.session.commit()
        self.mailer.non_selection(notice)
        return notice

    def qualify(self, account):
        try:
            return NonSelectionNotice.qualify(account)
        except SegueError, e:
            return False, None

    def get_by_hash(self, hash_code):
        return NonSelectionNotice.query.filter(NonSelectionNotice.hash == hash_code).first()

    def products_for(self, account):
        products = ProponentProduct.query.order_by(ProponentProduct.original_deadline).all()
        return [ p for p in products if p.check_eligibility({}, account) ]

class ProposalService(object):
    def __init__(self, db_impl=None, deadline=None, accounts=None, notifications=None):
        self.db = db_impl or db
        self.filter_strategies = ProposalFilterStrategies()
        self.deadline = deadline or CallForPapersDeadline()
        self.accounts = accounts or AccountService()
        self.notifications = notifications

    def cfp_state(self):
        return 'closed' if self.deadline.is_past() else 'open'

    def all_with_tags(self, *tags):
        return Proposal.query.join(ProposalTag).filter(ProposalTag.name.in_(tags)).order_by(Proposal.id).all()

    def create(self, data, owner, enforce_deadline=True):
        if enforce_deadline:
            self.deadline.enforce()
        if isinstance(owner, int):
            owner = self.accounts.get_one(owner, check_owner=False, strict=True)

        proposal = ProposalFactory.from_json(data, schema.new_proposal)
        proposal.owner = owner
        db.session.add(proposal)
        db.session.commit()
        return proposal

    def get_one(self, proposal_id, strict=False):
        proposal = Proposal.query.get(proposal_id)
        if proposal: return proposal
        elif strict: raise NoSuchProposal()
        return None

    def query(self, **kw):
        base        = self.filter_strategies.joins_for(Proposal.query, **kw)
        filter_list = self.filter_strategies.given(**kw)
        return base.filter(*filter_list).all()

    def count(self, **kw):
        base        = self.filter_strategies.joins_for(Proposal.query, **kw)
        filter_list = self.filter_strategies.given(**kw)
        return base.filter(*filter_list).count()

    def lookup(self, as_user=None, **kw):
        needle = kw.pop('q',None)
        limit  = kw.pop('limit',None)
        filter_list = self.filter_strategies.needle(needle, as_user, **kw)
        return Proposal.query.filter(*filter_list).limit(limit).all()

    def modify(self, proposal_id, data, by=None):
        self.deadline.enforce()

        proposal = self.get_one(proposal_id)
        if not self.check_ownership(proposal, by): raise NotAuthorized

        for name, value in ProposalFactory.clean_for_update(data).items():
            setattr(proposal, name, value)
        db.session.add(proposal)
        db.session.commit()
        return proposal

    def tag_proposal(self, proposal_id, tag_name):
        proposal = self.get_one(proposal_id)
        if proposal.tagged_as(tag_name): return proposal

        tag = ProposalTag(name=tag_name, proposal=proposal)
        db.session.add(tag)
        db.session.commit()
        return proposal

    def untag_proposal(self, proposal_id, tag_name):
        proposal = self.get_one(proposal_id)
        if not proposal.tagged_as(tag_name): return proposal

        tag = ProposalTag.query.filter(ProposalTag.name == tag_name, ProposalTag.proposal_id == proposal.id).first()
        db.session.delete(tag)
        db.session.commit()
        return proposal

    def check_ownership(self, proposal, alleged):
        if isinstance(proposal, int): proposal = self.get_one(proposal)
        return proposal and alleged and proposal.owner_id == alleged.id

    def list_tracks(self):
        return Track.query.all()

    def get_track(self, track_id):
        return Track.query.filter(Track.id == track_id).first()

    def by_coauthor(self, coauthor_id):
        return Proposal.query.filter(Proposal.invites.any(recipient=coauthor_id)).all()

    def set_status(self, proposal_id, new_status):
        proposal = self.get_one(proposal_id)
        proposal.status = new_status
        db.session.add(proposal)
        db.session.commit()
        return proposal

    def change_track(self, proposal_id, new_track_id):
        proposal = self.get_one(proposal_id)
        proposal.track_id = new_track_id
        db.session.add(proposal)
        db.session.commit()
        return proposal

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
        return proposal.invites[:]

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

    def set_coauthors(self, proposal_id, coauthor_ids):
        proposal = self.proposals.get_one(proposal_id, strict=True)
        existing_set = { a.id for a in proposal.coauthor_accounts }
        wanted_set   = set(coauthor_ids)

        for acc_id in wanted_set - existing_set:
            account = self.accounts.get_one(acc_id, strict=True, check_owner=False)
            invite = InviteFactory.for_account(proposal, account)
            db.session.add(invite)

        for acc_id in existing_set - wanted_set:
            account = self.accounts.get_one(acc_id, strict=True, check_owner=False)
            invite = ProposalInvite.query.filter(ProposalInvite.proposal == proposal, ProposalInvite.recipient == account.email).first()
            db.session.delete(invite)

        db.session.commit()

        return proposal



