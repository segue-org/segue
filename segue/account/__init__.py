from ..core import db
from ..factory import Factory
from ..json import jsoned

from models import Account

import schema

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


class AccountController(object):
    @jsoned
    def schema(self, name):
        return schema.whitelist[name]

    def create(self):
        data = request.get_json();
