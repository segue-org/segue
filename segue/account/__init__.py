from flask import request, url_for, redirect
from sqlalchemy.orm.exc import NoResultFound

from ..core import db
from ..factory import Factory
from ..json import jsoned
from ..errors import InvalidLogin

from jwt import Signer

from models import Account
import schema


class AccountFactory(Factory):
    model = Account

    UPDATE_WHITELIST = schema.signup["properties"].keys()

    @classmethod
    def clean_for_insert(cls, data):
        data = { c:v for c,v in data.items() if c in AccountFactory.UPDATE_WHITELIST }
        data['document'] = data.pop('cpf', None) or data.pop('passport', None)
        return data;

class AccountService(object):
    def __init__(self, db_impl=None, signer=None):
        self.db     = db_impl or db
        self.signer = signer or Signer()

    def get_one(self, id):
        return Account.query.get(id)

    def create(self, data):
        account = AccountFactory.from_json(data, schema.signup)
        db.session.add(account)
        db.session.commit()
        return account

    def login(self, email=None, password=None):
        try:
            account = Account.query.filter(Account.email == email).one()
            if account.password == password:
                return self.signer.sign(account)
            raise InvalidLogin()
        except NoResultFound, e:
            raise InvalidLogin()

class AccountController(object):
    def __init__(self, service=None):
        self.service = service or AccountService()

    @jsoned
    def schema(self, name):
        return schema.whitelist[name]

    @jsoned
    def create(self):
        data = request.get_json()
        return self.service.create(data), 201

    @jsoned
    def login(self):
        data = request.get_json()
        return self.service.login(**data), 200

    def list_proposals(self, account_id):
        query_string = "?owner_id={}".format(account_id)
        return redirect(url_for('proposals.list') + query_string)
