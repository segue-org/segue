import datetime

from sqlalchemy.sql import functions as func

from ..json import JsonSerializable, SQLAlchemyJsonSerializer
from ..core import db

import schema

class ProposalJsonSerializer(SQLAlchemyJsonSerializer):
    def serialize_child(self, child):
        if child == 'owner':
            return 'SafeAccountJsonSerializer'
        return False

class Proposal(JsonSerializable, db.Model):
    _serializers = [ ProposalJsonSerializer ]

    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.Text)
    summary      = db.Column(db.Text)
    full         = db.Column(db.Text)
    language     = db.Column(db.String(100))
    level        = db.Column(db.Enum(*schema.PROPOSAL_LEVELS, name="proposal_levels"))
    owner_id     = db.Column(db.Integer, db.ForeignKey('account.id'))
    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)

    invites      = db.relationship("ProposalInvite", backref="proposal")

class InviteJsonSerializer(SQLAlchemyJsonSerializer):
    def serialize_child(self, child):
        return dict(proposal='ProposalJsonSerializer').get(child, False)

class ShortInviteJsonSerializer(InviteJsonSerializer):
    def serialize_child(self, child):
        return False;

class SafeInviteJsonSerializer(InviteJsonSerializer):
    def hide_field(self, child):
        return child in ['recipient']

class ProposalInvite(JsonSerializable, db.Model):
    _serializers = [ InviteJsonSerializer, ShortInviteJsonSerializer, SafeInviteJsonSerializer ]

    id           = db.Column(db.Integer, primary_key=True)
    hash         = db.Column(db.String(64))
    proposal_id  = db.Column(db.Integer, db.ForeignKey('proposal.id'))
    recipient    = db.Column(db.Text)
    name         = db.Column(db.Text)
    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    status       = db.Column(db.Enum('pending','accepted','declined', 'cancelled', name='invite_statuses'))
