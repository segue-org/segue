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
        return child in [ 'password','email','role', 'phone', 'city', 'document' ]

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

    proposals    = db.relationship("Proposal", backref="owner")
