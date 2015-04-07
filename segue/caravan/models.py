import datetime
from sqlalchemy.sql import functions as func
from ..core import db
from ..json import JsonSerializable

from serializers import *

class Caravan(JsonSerializable, db.Model):
    _serializers = [ CaravanJsonSerializer ]
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.Text)
    city         = db.Column(db.Text)
    owner_id     = db.Column(db.Integer, db.ForeignKey('account.id'))
    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    invites      = db.relationship("CaravanInvite", backref="caravan")

class CaravanInvite(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    hash         = db.Column(db.String(64))
    caravan_id   = db.Column(db.Integer, db.ForeignKey('caravan.id'))
    recipient    = db.Column(db.Text)
    name         = db.Column(db.Text)
    account      = db.Column(db.Integer, db.ForeignKey('account.id'))
    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    status       = db.Column(db.Enum('pending','accepted','declined', 'cancelled', name='invite_statuses'),default='pending')
