from sqlalchemy.orm.exc import NoResultFound

from flask import request, current_app
from werkzeug.local import LocalProxy

from ..core import db
from ..factory import Factory
from ..json import jsoned

from models import Account, AuthEnvelope
import schema

local_jwt = LocalProxy(lambda: current_app.extensions['jwt'])

class AccountFactory(Factory):
    model = Account

class AccountService(object):
    def __init__(self, db_impl=None):
        self.db = db_impl or db

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
                return AuthEnvelope(account, jwt=local_jwt)
            raise NoResultFound()
        except NoResultFound, e:
            print e

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
