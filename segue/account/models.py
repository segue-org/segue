import datetime

from sqlalchemy_utils.types.password import PasswordType
from sqlalchemy.sql import functions as func

from ..json import JsonSerializable, SQLAlchemyJsonSerializer
from ..core import db

import schema

class AccountJsonSerializer(SQLAlchemyJsonSerializer):
    _serializer_name = 'normal'
    def hide_field(self, child):
        return child == 'password'

    def serialize_child(self, child):
        return False

class SafeAccountJsonSerializer(AccountJsonSerializer):
    _serializer_name = 'safe'
    def hide_field(self, child):
        return child in [ 'password','email', 'role', 'phone', 'city', 'document' ]

class TokenJsonSerializer(AccountJsonSerializer):
    _serializer_name = 'token'
    def hide_field(self, child):
        return child not in [ 'id','email','role', 'name' ]

class Account(JsonSerializable, db.Model):
    _serializers = [ AccountJsonSerializer, SafeAccountJsonSerializer, TokenJsonSerializer ]

    id           = db.Column(db.Integer, primary_key=True)
    email        = db.Column(db.Text, unique=True)
    name         = db.Column(db.Text)
    password     = db.Column(PasswordType(schemes=['pbkdf2_sha512']))
    role         = db.Column(db.Enum(*schema.ACCOUNT_ROLES, name='account_roles'))
    document     = db.Column(db.Text)
    country      = db.Column(db.Text)
    state        = db.Column(db.Text)
    city         = db.Column(db.Text)
    phone        = db.Column(db.Text)
    organization = db.Column(db.Text)
    resume       = db.Column(db.Text)
    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)

    proposals     = db.relationship("Proposal", backref="owner")
    purchases     = db.relationship("Purchase", backref="customer")
    caravan_owned = db.relationship("Caravan",  backref="owner")

    def can_be_acessed_by(self, alleged):
        if not alleged: return False
        if self.id == alleged.id: return True
        if alleged.role == 'admin': return True
        return False

    @property
    def payments(self):
        payments = []
        for purchase in self.purchases:
            payments.extend(purchase.payments)
        return payments

class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    cctld = db.Column(db.Text)
    iso = db.Column(db.Integer)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.Text)
    name = db.Column(db.Text)
    latitude = db.Column(db.Numeric)
    longitude = db.Column(db.Numeric)

    __tablename__ = 'cities'

