from segue.core import db
from segue.errors import AccountAlreadyHasCorporate, NotAuthorized
from segue.hasher import Hasher
from segue.mailer import MailerService

import schema

from models import Corporate, CorporateEmployee
from factories import CorporateFactory, CorporateEmployeeFactory, CorporatePurchaseFactory
from ..account import AccountService, Account

class CorporateService(object):
    def __init__(self, employees=None):
        self.employees = employees or CorporateEmployeeService(corporates=self)

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

    def add_people(self, corporate_id, people, buyer_data, by=None):
        return self.employees.create(corporate_id, people, buyer_data, by=by)

    def sum_employee_tickets(self, corporate_id, product_value, by):
        value = 0
        for employee in self.employees.list(corporate_id, by=by):
            value += product_value

        return value

class CorporateEmployeeService(object):
    def __init__(self, corporates=None, accounts = None, hasher=None):
        self.corporates  = corporates  or CorporateService()
        self.accounts  = accounts  or AccountService()
        self.hasher = hasher or Hasher(10)

    def list(self, corporate_id, by=None):
        return self.corporates.get_one(corporate_id, by).employees

    def create(self, corporate_id, data, buyer_data, by=None):
        corporate = self.corporates.get_one(corporate_id, by)

        data['document'] = str(data['document']).translate(None, './-')

        account_data = {
            'email': data['email'],
            'name': data['name'],
            'cpf': data['document'],
            'country': buyer_data['address_country'],
            'city': buyer_data['address_city'],
            'phone': by.phone,
            'password': self.hasher.generate()
        }

        account = self.accounts.create(account_data)

        employee = CorporateEmployeeFactory.from_json(data, schema.new_employee)
        employee.corporate = corporate

        db.session.add(employee)
        db.session.commit()
        db.session.add(account)
        db.session.commit()

        return employee
