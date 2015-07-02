import datetime

from sqlalchemy import or_, and_
from sqlalchemy.sql import functions as func
from sqlalchemy.dialects import postgresql

from ..json import JsonSerializable
from ..core import db, logger
from .serializers import *

from segue.account.errors import NoSuchAccount, AccountAlreadyHasPurchase
from segue.product.models import Product

import schema

class ProposalTag(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.Text)
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposal.id'))

class Proposal(JsonSerializable, db.Model):
    _serializers = [ ProposalJsonSerializer, ShortChildProposalJsonSerializer ]

    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.Text)
    full         = db.Column(db.Text)
    language     = db.Column(db.String(100))
    level        = db.Column(db.Enum(*schema.PROPOSAL_LEVELS, name="proposal_levels"))
    owner_id     = db.Column(db.Integer, db.ForeignKey('account.id'))
    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    invites      = db.relationship("ProposalInvite", backref="proposal", lazy='dynamic')
    track_id     = db.Column(db.Integer, db.ForeignKey('track.id'))
    status       = db.Column(db.Text, server_default='proposal')

    tags          = db.relationship("ProposalTag", backref="proposal", lazy="dynamic")
    notifications = db.relationship("CallNotification", backref="proposal", lazy="dynamic")
    slots         = db.relationship("Slot", backref="talk", lazy="dynamic")

    as_player1 = db.relationship("Match", backref="player1", lazy="dynamic", foreign_keys="Match.player1_id")
    as_player2 = db.relationship("Match", backref="player2", lazy="dynamic", foreign_keys="Match.player2_id")

    def can_be_acessed_by(self, alleged):
        if not alleged: return False
        if self.owner.id == alleged.id: return True
        if alleged.role == 'admin': return True
        return False

    @property
    def related_emails(self):
        return set([ self.owner.email ] + [ x.recipient for x in self.coauthors ])

    @property
    def slotted(self):
        return self.slots.count() > 0

    @property
    def coauthors(self):
        return self.invites.filter(ProposalInvite.status == 'accepted')

    @property
    def coauthor_accounts(self):
        return [ x.account for x in self.coauthors.all() ]

    @property
    def tag_names(self):
        return [ tag.name for tag in self.tags.all() ]

    @property
    def is_talk(self):
        return self.status == 'confirmed'

    def tagged_as(self, tag_name):
        return tag_name in self.tag_names

class ProposalInvite(JsonSerializable, db.Model):
    _serializers = [ InviteJsonSerializer, ShortInviteJsonSerializer, SafeInviteJsonSerializer ]

    id           = db.Column(db.Integer, primary_key=True)
    hash         = db.Column(db.String(64))
    proposal_id  = db.Column(db.Integer, db.ForeignKey('proposal.id'))
    recipient    = db.Column(db.Text)
    name         = db.Column(db.Text)
    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    status       = db.Column(db.Enum('pending','accepted','declined', 'cancelled', name='invite_statuses'),default='pending')

    account = db.relation('Account', uselist=False,
        backref=db.backref('proposal_invites', uselist=True),
        primaryjoin='Account.email == ProposalInvite.recipient',
        foreign_keys='Account.email')

class Track(JsonSerializable, db.Model):
    _serializers = [ TrackSerializer, ShortTrackSerializer ]

    id           = db.Column(db.Integer, primary_key=True)
    name_pt      = db.Column(db.Text)
    name_en      = db.Column(db.Text)
    public       = db.Column(db.Boolean, default=True)

    proposals    = db.relationship("Proposal", backref="track")


class ProponentProduct(Product):
    original_deadline = db.Column(db.DateTime)
    __mapper_args__ = { 'polymorphic_identity': 'proponent' }

    def check_eligibility(self, buyer_data, account=None):
        was_not_accepted, earliest_proposal = NonSelectionNotice.qualify(account)

        if not was_not_accepted: return False

        timely_proponent  = earliest_proposal.created < self.original_deadline
        return was_not_accepted and timely_proponent

class StudentProponentProduct(ProponentProduct):
    __mapper_args__ = { 'polymorphic_identity': 'proponent-student' }

class SpeakerProduct(Product):
    __mapper_args__ = { 'polymorphic_identity': 'speaker' }

class NonSelectionNotice(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    hash       = db.Column(db.String(64))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))

    account    = db.relationship("Account")

    @classmethod
    def qualify(cls, account):
        if not account: raise NoSuchAccount()
        if account.has_valid_purchases: raise AccountAlreadyHasPurchase()

        coauthorship = Proposal.invites.any(and_(ProposalInvite.recipient == account.email, ProposalInvite.status == 'accepted'))

        proposals_owned      = Proposal.query.filter(Proposal.owner == account).all()
        proposals_coauthored = Proposal.query.filter(coauthorship).all()
        proposals_involved = proposals_owned + proposals_coauthored

        if not proposals_involved: return False, None
        # logger.debug('-- proposals: owned %s, coauthored %s', len(proposals_owned), len(proposals_coauthored))

        proposals_judged    = filter(lambda x: x.tagged_as('player'), proposals_involved)
        proposals_confirmed = filter(lambda x: x.is_talk,             proposals_involved)
        # logger.debug('-- proposals: judged %s, confirmed %s', len(proposals_judged), len(proposals_confirmed))

        was_not_accepted = len(proposals_judged) > 0 and len(proposals_confirmed) == 0
        # logger.debug('-- was not accepted? %s', was_not_accepted)
        earliest_proposal = min(proposals_involved, key=lambda x: x.created)
        # logger.debug('-- earliest submission was %s', earliest_proposal.created)

        return was_not_accepted, earliest_proposal

