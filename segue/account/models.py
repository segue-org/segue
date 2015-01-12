from ..json import SQLAlchemyJsonSerializer
from ..core import db

import schema

class AccountJsonSerializer(SQLAlchemyJsonSerializer):
    __json_public__ = [ 'id', 'email', 'role' ]

class Account(AccountJsonSerializer, db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    email    = db.Column(db.Text)
    name     = db.Column(db.Text)
    password = db.Column(db.Text)
    role     = db.Column(db.Enum(*schema.ACCOUNT_ROLES))
