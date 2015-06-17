from datetime import datetime, timedelta
from sqlalchemy.sql import functions as func
from segue.core import db

SLOT_STATUSES = ('confirmed','pending','rejected','dirty','empty');

class Room(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    position    = db.Column(db.Integer)
    name        = db.Column(db.Text)
    capacity    = db.Column(db.Integer)
    translation = db.Column(db.Boolean, default=False)

    slots       = db.relationship("Slot", backref="room")

class Slot(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    room_id     = db.Column(db.Integer, db.ForeignKey('room.id'))
    talk_id     = db.Column(db.Integer, db.ForeignKey('proposal.id'))
    blocked     = db.Column(db.Boolean, default=False)
    begins      = db.Column(db.DateTime)
    duration    = db.Column(db.Integer)
    status      = db.Column(db.Enum(*SLOT_STATUSES, name="slot_statuses"), default='empty')

    talk        = db.relationship("Talk", backref="slot")

    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.now)
