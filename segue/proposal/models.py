import datetime

from sqlalchemy.sql import functions as func

from ..json import JsonSerializable, SQLAlchemyJsonSerializer
from ..core import db

import schema

class ProposalJsonSerializer(SQLAlchemyJsonSerializer):
    _serializer_name = 'normal'
    _child_serializers = dict(owner='SafeAccountJsonSerializer')
    def serialize_child(self, child):
        return self._child_serializers.get(child, False)

class ShortChildProposalJsonSerializer(ProposalJsonSerializer):
    _serializer_name = 'short_child'
    _child_serializers = dict(owner='SafeAccountJsonSerializer', invites='ShortInviteJsonSerializer')

class Proposal(JsonSerializable, db.Model):
    _serializers = [ ProposalJsonSerializer, ShortChildProposalJsonSerializer ]

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
    _serializer_name = 'normal'
    def serialize_child(self, child):
        return dict(proposal='ProposalJsonSerializer').get(child, False)

class ShortInviteJsonSerializer(InviteJsonSerializer):
    _serializer_name = 'short'
    def serialize_child(self, child):
        return False;

class SafeInviteJsonSerializer(InviteJsonSerializer):
    _serializer_name = 'safe'
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
    status       = db.Column(db.Enum('pending','accepted','declined', 'cancelled', name='invite_statuses'),default='pending')
