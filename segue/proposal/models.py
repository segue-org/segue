import datetime

from sqlalchemy.sql import functions as func

from ..json import JsonSerializable, SQLAlchemyJsonSerializer
from ..core import db

import schema

class ProposalJsonSerializer(SQLAlchemyJsonSerializer):
    def override_children(self):
        from ..models import SafeAccountJsonSerializer
        self.override_child('owner', SafeAccountJsonSerializer)

class Proposal(JsonSerializable, db.Model):
    _serializer = ProposalJsonSerializer

    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.Text)
    summary      = db.Column(db.Text)
    full         = db.Column(db.Text)
    language     = db.Column(db.String(100))
    level        = db.Column(db.Enum(*schema.PROPOSAL_LEVELS, name="proposal_levels"))
    owner_id     = db.Column(db.Integer, db.ForeignKey('account.id'))
    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)
