from sqlalchemy_utils.types.password import PasswordType

from ..json import SQLAlchemyJsonSerializer, PropertyJsonSerializer
from ..core import db

import schema

class AccountJsonSerializer(SQLAlchemyJsonSerializer):
    __json_public__ = [ 'id', 'email', 'name', 'role' ]

class Account(AccountJsonSerializer, db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    email        = db.Column(db.Text, unique=True)
    name         = db.Column(db.Text)
    password     = db.Column(PasswordType(schemes=['pbkdf2_sha512']))
    role         = db.Column(db.Enum(*schema.ACCOUNT_ROLES, name='account_roles'))
    country      = db.Column(db.Text)
    state        = db.Column(db.Text)
    city         = db.Column(db.Text)
    phone        = db.Column(db.Text)
    organization = db.Column(db.Text)
    resume       = db.Column(db.Text)

    proposals    = db.relationship("Proposal", backref="owner")
