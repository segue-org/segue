from datetime import datetime, timedelta
from sqlalchemy.orm import backref
from sqlalchemy.sql import functions as func
from ..core import db

SLOT_STATUSES = ('confirmed','pending','rejected','declined','dirty','empty');

class Room(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    position    = db.Column(db.Integer)
    name        = db.Column(db.Text)
    capacity    = db.Column(db.Integer)
    translation = db.Column(db.Boolean, default=False)

    slots       = db.relationship("Slot", backref="room")

class Recording(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    slot_id = db.Column(db.Integer, db.ForeignKey('slot.id'))
    url     = db.Column(db.Text)

class Slot(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    room_id     = db.Column(db.Integer, db.ForeignKey('room.id'))
    talk_id     = db.Column(db.Integer, db.ForeignKey('proposal.id'))
    blocked     = db.Column(db.Boolean, default=False)
    begins      = db.Column(db.DateTime)
    duration    = db.Column(db.Integer)
    status      = db.Column(db.Enum(*SLOT_STATUSES, name="slot_statuses"), default='empty')
    annotation  = db.Column(db.Text)

    notifications = db.relationship("SlotNotification", backref="slot", lazy="dynamic")
    recordings    = db.relationship("Recording",        backref="slot", lazy="dynamic")

    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.now)

    def __repr__(self):
        return "<[{}]{}:{}+{}:{}>".format(self.id, self.room.name, self.begins, self.duration, self.talk != None)

    @property
    def next_contiguous_slot(self):
        same_room   = Slot.query.filter(Slot.room == self.room)
        my_end_hour = self.begins + timedelta(minutes=self.duration)
        return same_room.filter(Slot.begins == my_end_hour).first()

    @property
    def can_be_stretched(self):
        next_slot = self.next_contiguous_slot
        if not next_slot: return True
        return next_slot.talk == None

    @property
    def can_be_unstretched(self):
        return self.duration > 60

class Notification(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    kind       = db.Column(db.Text)
    hash       = db.Column(db.String(64))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    content    = db.Column(db.Text)
    sent       = db.Column(db.DateTime)
    deadline   = db.Column(db.DateTime)
    status     = db.Column(db.Enum('confirmed', 'pending', 'declined'))

    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.now)

    account = db.relationship('Account')

    __tablename__ = 'notification'
    __mapper_args__ = { 'polymorphic_on': kind, 'polymorphic_identity': 'notification' }

    @property
    def is_expired(self):
        return self.status == 'pending' and (datetime.now() > self.deadline)


class CallNotification(Notification):
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposal.id'), name='cn_proposal_id')
    __mapper_args__ = { 'polymorphic_identity': 'call' }

    def update_target_status(self):
        self.proposal.status = self.status
        return self.proposal

    @property
    def target(self):
        return self.proposal

class SlotNotification(Notification):
    slot_id         = db.Column(db.Integer, db.ForeignKey('slot.id'), name='sn_slot_id')
    __mapper_args__ = { 'polymorphic_identity': 'slot' }

    def update_target_status(self):
        self.slot.status = self.status
        return self.slot
