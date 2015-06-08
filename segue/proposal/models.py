import datetime

from sqlalchemy.sql import functions as func
from sqlalchemy.dialects import postgresql

from ..json import JsonSerializable
from ..core import db
from .serializers import *

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

    tags = db.relationship("ProposalTag", backref="proposal", lazy="dynamic")

    as_player1 = db.relationship("Match", backref="player1", lazy="dynamic", foreign_keys="Match.player1_id")
    as_player2 = db.relationship("Match", backref="player2", lazy="dynamic", foreign_keys="Match.player2_id")

    @property
    def coauthors(self):
        return self.invites.filter(ProposalInvite.status == 'accepted')

    @property
    def tag_names(self):
        return [ tag.name for tag in self.tags.all() ]

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
