from segue.core import db
from segue.hasher import Hasher
from segue.mailer import MailerService

import schema

from models import Corporate, EmployeeAccount
from factories import CorporateFactory, EmployeeAccountFactory, CorporatePurchaseFactory
from errors import AccountAlreadyHasCorporate

from ..account import schema as account_schema
from segue.account.errors import NotAuthorized

class CorporateService(object):
    def __init__(self, employees=None):
        self.employees = employees or EmployeeAccountService(corporates=self)

    def get_one(self, corporate_id, by=None):
        result = Corporate.query.get(corporate_id)
        if self._check_ownership(result, by):
            return result
        elif result:
            raise NotAuthorized()

    def _check_ownership(self, corporate, alleged):
        if isinstance(corporate, int): corporate = self.get_one(corporate)
        return corporate and alleged and corporate.owner_id == alleged.id

    def get_by_owner(self, owner_id, by=None):
        result = Corporate.query.filter(Corporate.owner_id == owner_id).first()
        if self._check_ownership(result, by):
            return result
        elif result:
            raise NotAuthorized()

    def create(self, data, owner):
        if self.get_by_owner(owner.id, owner): raise AccountAlreadyHasCorporate()

        corporate = CorporateFactory.from_json(data, schema.new_corporate)
        corporate.owner_id = owner.id

        db.session.add(corporate)
        db.session.commit()
        return corporate

    def modify(self, corporate_id, data, by=None):
        corporate = self.get_one(corporate_id, by)

        for name, value in CorporateFactory.clean_for_update(data).items():
            setattr(corporate, name, value)
        db.session.add(corporate)
        db.session.commit()
        return corporate

    def add_person(self, corporate_id, account, by=None):
        account.corporate = self.get_one(corporate_id)
        db.session.add(account)
        return account

    def sum_employee_tickets(self, corporate_id, product_value, by):
        value = 0
        for employee in self.employees.list(corporate_id, by=by):
            value += product_value

        return value

class EmployeeAccountService(object):
    def __init__(self, corporates=None, hasher=None):
        self.corporates  = corporates  or CorporateService()
        self.hasher = hasher or Hasher(10)
        self.account_schema = account_schema

    def list(self, corporate_id, by=None):
        return self.corporates.get_one(corporate_id, by).employees

    def create(self, corporate_id, data, by=None):
        corporate = self.corporates.get_one(corporate_id, by)

        data['document'] = str(data['document']).translate(None, './-')

        account_data = {
            'email': data['email'],
            'name': data['name'],
            'document': data['document'],
            'password': self.hasher.generate(),
            'corporate_id': corporate.id
        }

        account = EmployeeAccountFactory.from_json(account_data, self.account_schema.signup)

        db.session.add(account)
        db.session.commit()
        return account
