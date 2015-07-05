import datetime
from sqlalchemy.sql import functions as func
from ..core import db
from ..json import JsonSerializable
from segue.purchase.models import Purchase, Payment, Transition
from segue.account.models import Account
from segue.product.errors import WrongBuyerForProduct

from serializers import *

class Corporate(JsonSerializable, db.Model):
    _serializers     = [ CorporateJsonSerializer ]
    id               = db.Column(db.Integer, primary_key=True)
    owner_id         = db.Column(db.Integer, db.ForeignKey('account.id'))
    kind             = db.Column(db.Text, server_default='corporate')

    name             = db.Column(db.Text)
    badge_name       = db.Column(db.Text)
    document         = db.Column(db.Text)
    address_street   = db.Column(db.Text)
    address_number   = db.Column(db.Text)
    address_extra    = db.Column(db.Text)
    address_district = db.Column(db.Text)
    address_city     = db.Column(db.Text)
    address_state    = db.Column(db.Text)
    address_zipcode  = db.Column(db.Text)
    incharge_name    = db.Column(db.Text)
    incharge_email   = db.Column(db.Text)
    incharge_phone_1 = db.Column(db.Text)
    incharge_phone_2 = db.Column(db.Text)

    created          = db.Column(db.DateTime, default=func.now())
    last_updated     = db.Column(db.DateTime, onupdate=datetime.datetime.now)

    employees        = db.relationship('Account', backref='corporate')

    __mapper_args__ = { 'polymorphic_on': kind, 'polymorphic_identity': 'business' }

EmployeeAccount = Account

class GovCorporate(Corporate):
    __mapper_args__ = { 'polymorphic_identity': 'government' }

class CorporatePurchase(Purchase):
    __mapper_args__ = { 'polymorphic_identity': 'corporate' }
    corporate_id = db.Column(db.Integer, db.ForeignKey('corporate.id'), name='cr_corporate_id')

class EmployeePurchase(CorporatePurchase):
    __mapper_args__ = { 'polymorphic_identity': 'employee' }

class DepositPayment(Payment):
    __mapper_args__ = { 'polymorphic_identity': 'deposit' }

class DepositTransition(Transition):
    __mapper_args__ = { 'polymorphic_identity': 'deposit' }

class GovPayment(Payment):
    __mapper_args__ = { 'polymorphic_identity': 'government' }

class GovTransition(Transition):
    __mapper_args__ = { 'polymorphic_identity': 'government' }
