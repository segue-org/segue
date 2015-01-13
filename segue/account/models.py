from sqlalchemy_utils.types.password import PasswordType

from ..json import SQLAlchemyJsonSerializer, PropertyJsonSerializer
from ..core import db

import schema

class AccountJsonSerializer(SQLAlchemyJsonSerializer):
    __json_public__ = [ 'id', 'email', 'role' ]

class Account(AccountJsonSerializer, db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    email    = db.Column(db.Text)
    name     = db.Column(db.Text)
    password = db.Column(PasswordType(schemes=['pbkdf2_sha512']))
    role     = db.Column(db.Enum(*schema.ACCOUNT_ROLES))

class AuthEnvelope(PropertyJsonSerializer):
    def get_field_names(self):
        return ['account', 'token']

    def __init__(self, account, jwt=None):
        self.account = account.to_json()
        self.token   = jwt.encode_callback(self.account)
