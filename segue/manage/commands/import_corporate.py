# -*- coding: utf-8 -*-
import codecs, os
import datetime
import tablib
import json
import yaml
import sys

from segue.core import db
from segue.hasher import Hasher
from segue.models import *
from segue.product.services import ProductService
from segue.corporate.services import CorporateService, EmployeeAccountService
from segue.account.services import AccountService
from segue.purchase.services import PurchaseService
from segue.purchase.boleto.models import BoletoPayment, BoletoTransition
from segue.mailer import MailerService

ds = tablib.Dataset()

product_service = ProductService()
corporate_service = CorporateService()
employee_service = EmployeeAccountService()
account_service = AccountService()
purchase_service = PurchaseService()
mailer_service = MailerService()

counter = 0
counter_added = 0

def import_corporate(in_file, file_type):
    global counter, counter_added

    with open(in_file, "r") as f:
        ds.csv = f.read()

    counter = 0
    counter_added = 0
    for item in ds.dict:
        if file_type == 'government':
            process_line_gov(item)
        elif file_type == 'business':
            process_line_business(item)
        else:
            print "Error: file_type not recognized."
            sys.exit()

    print "###########################################################"
    print "records processed: ", counter
    print "records inserted:  ", counter_added
    print "####################### DONE! #############################"

def format_date(date):
    items = date.split("/")
    return datetime.date(int(items[2]), int(items[1]), int(items[0]))

def generate_password():
    h = Hasher(8)
    return h.generate()

def process_line_business(item):
    global counter, counter_added
    #header definition
    # fields starting with '_' will be ignored
    # fields starting with '*' will be used programatically

    # Corporate:
    # _id, _data_envio, *pago, document, name, badge_name, address_street,
    # address_number, address_extra, address_district, address_zipcode,
    # address_city, address_state, _issqn, incharge_name, incharge_email,
    # incharge_phone_1, incharge_phone_2, *participants, _, (employee_data here)

    # if *pago == "SIM":
    # CorporatePayment
    # our_number, payment_date, amount

    # for n in xrange(participants):
        # EmployeeAccount
        # name_<n>, badge_name_<n>, document_<n>, email_<n>

    # CorporatePurchase:
    # _boleto_emitido, _nf_emitida, payment_date, amount, our_number, description, _details

    corp_data = item.copy()
    employees = []

    counter += 1
    if item['*pago'] == "SIM":
        del corp_data['_id']
        del corp_data['_data_envio']
        del corp_data['*pago']
        del corp_data['_issqn']
        del corp_data['*participants']
        del corp_data['_']

        # 16 -> number of employees slots in csv file
        for n in xrange(1, 17):
            if corp_data['name_{}'.format(n)] != '':
                employee = {
                    'name':       corp_data['name_{}'.format(n)],
                    'badge_name': corp_data['badge_name_{}'.format(n)],
                    'document':   corp_data['document_{}'.format(n)],
                    'email':      corp_data['email_{}'.format(n)],
                }
                print "adding employee: ", employee
                employees.append(employee)
            del corp_data['name_{}'.format(n)]
            del corp_data['badge_name_{}'.format(n)]
            del corp_data['document_{}'.format(n)]
            del corp_data['email_{}'.format(n)]

        if '' in corp_data:
            del corp_data['']

        del corp_data['_boleto_emitido']
        del corp_data['_nf_emitida']
        del corp_data['_details']

        del corp_data['payment_date']
        del corp_data['amount']
        del corp_data['our_number']
        del corp_data['description']
        #del corp_data['_details']

        corp_data = dict((k, v) for k, v in corp_data.iteritems() if v)

        print "adding/getting corporate: ", corp_data['name']
        owner = get_or_add_account_owner({
            'name': corp_data['incharge_name'],
            'email': corp_data['incharge_email'],
            'document': '00000000000',
            'city': corp_data['address_city'],
            'phone': corp_data['incharge_phone_1']
        })
        print corp_data
        if owner.corporate_owned:
            corporate = owner.corporate_owned[0]
        else:
            corporate = corporate_service.create(corp_data, owner)

        for e in employees:
            e['corporate_id'] = corporate.id
            "adding/getting employee: ", e['email']
            if account_service.is_email_registered(e['email']):
                employee = Account.query.filter(Account.email == e['email']).first()
                employee.role = 'employee'
                employee.corporate_id = corporate.id
            else:
                employee = EmployeeAccount(**e)

            db.session.add(employee)

        # add purchase/payment
        db.session.commit()

        print corp_data
        print "###################### employees: "
        print employees

        counter_added +=1

def process_line_gov(item):
    #header definition
    # fields starting with '_' will be ignored
    # fields starting with '*' will be used programatically

    # if *nota_empenho == "SIM":
    # GovCorporate:
    # _id, _data_envio, *nota_empenho, _idioma_inicial, _data_inicio, _data_ultima_acao,
    # document, name, badge_name, address_street, address_number, address_extra,
    # address_district, address_zipcode, address_city, address_state, _issqn,
    # incharge_name, incharge_email, incharge_phone_1, incharge_phone_2,
    # *participants, _, (employee_data here)

    # for n in xrange(participants):
        # EmployeeAccount
        # name_<n>, badge_name_<n>, document_<n>, email_<n>

    # CorporatePurchase
    # description

    print item

def get_or_add_account_owner(item):
    h = Hasher(10)

    account_data = {
        'name': item['name'],
        'email': item['email'],
        'document': item['document'],
        'password': h.generate(),
        'country': 'BRASIL',
        'city': item['city'],
        'phone': item['phone']
    }

    if account_service.is_email_registered(account_data['email']):
        return Account.query.filter(Account.email == account_data['email']).one()
    else:
        return account_service.create(account_data)
