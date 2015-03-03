from flask import request, url_for, redirect
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from flask.ext.jwt import current_user, verify_jwt, JWTError

from ..core import db, jwt_required
from ..factory import Factory
from ..json import jsoned
from ..errors import InvalidLogin, EmailAlreadyInUse, NotAuthorized

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

    @classmethod
    def clean_for_update(cls, data):
        update_whitelist = AccountFactory.UPDATE_WHITELIST[:]
        update_whitelist.remove('email')
        data = { c:v for c,v in data.items() if c in update_whitelist }
        data['document'] = data.pop('cpf', None) or data.pop('passport', None)
        return data;

class AccountService(object):
    def __init__(self, db_impl=None, signer=None):
        self.db     = db_impl or db
        self.signer = signer or Signer()

    def is_email_registered(self, email):
        return Account.query.filter(Account.email == email).count() > 0

    def get_one(self, id, by=None, check_owner=True):
        account = self._get_account(id)
        if check_owner and not self.check_ownership(account, by): raise NotAuthorized
        return account

    def _get_account(self, id):
        return Account.query.get(id)

    def modify(self, account_id, data, by=None):
        account = self._get_account(account_id)
        if not self.check_ownership(account, by): raise NotAuthorized

        for name, value in AccountFactory.clean_for_update(data).items():
            setattr(account, name, value)
        db.session.add(account)
        db.session.commit()
        return account

    def check_ownership(self, account, alleged):
        if isinstance(account, int): account = self._get_account(id)
        return account and alleged and account.id == alleged.id

    def create(self, data):
        try:
            account = AccountFactory.from_json(data, schema.signup)
            db.session.add(account)
            db.session.commit()
            return account
        except IntegrityError, e:
            raise EmailAlreadyInUse(account.email)

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
        self.current_user = current_user

    @jwt_required()
    @jsoned
    def get_one(self, account_id):
        result = self.service.get_one(account_id, by=self.current_user) or flask.abort(404)
        return result, 200

    @jwt_required()
    @jsoned
    def modify(self, account_id):
        data = request.get_json()
        result = self.service.modify(account_id, data, by=self.current_user) or flask.abort(404)
        return result, 200

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
