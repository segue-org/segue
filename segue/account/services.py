from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

from ..core import db
from ..errors import InvalidLogin, EmailAlreadyInUse, NotAuthorized
from ..filters import FilterStrategies

from jwt import Signer

from models import Account
from factories import AccountFactory
import schema

class AccountFilterStrategies(FilterStrategies):
    def by_id(self, value):
        if value.isdigit():
            return Account.id == value

    def by_email(self, value):
        return Account.email.ilike('%'+value+'%')

    def by_name(self, value):
        return Account.name.ilike('%'+value+'%')

    def by_document(self, value):
        return Account.document.like('%'+value+'%')

class AccountService(object):
    def __init__(self, db_impl=None, signer=None):
        self.db     = db_impl or db
        self.signer = signer or Signer()
        self.filters = AccountFilterStrategies()

    def is_email_registered(self, email):
        return Account.query.filter(Account.email == email).count() > 0

    def get_one(self, account_id, by=None, check_owner=True):
        account = self._get_account(account_id)
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

    def lookup(self, needle, by=None):
        filters = self.filters.needle(needle, by)
        return Account.query.filter(or_(*filters)).all()

    def check_ownership(self, account, alleged):
        if isinstance(account, int): account = self._get_account(id)
        return account and account.can_be_acessed_by(alleged)

    def create(self, data):
        try:
            account = AccountFactory.from_json(data, schema.signup)
            db.session.add(account)
            db.session.commit()
            return account
        except IntegrityError:
            raise EmailAlreadyInUse(account.email)

    def login(self, email=None, password=None):
        try:
            account = Account.query.filter(Account.email == email).one()
            if account.password == password:
                return self.signer.sign(account)
            raise InvalidLogin()
        except NoResultFound:
            raise InvalidLogin()

