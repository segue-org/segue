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
            if corp_data['name_{}'.format(n)] == '':
                del corp_data['name_{}'.format(n)]
                del corp_data['badge_name_{}'.format(n)]
                del corp_data['document_{}'.format(n)]
                del corp_data['email_{}'.format(n)]
            else:
                employees.append({
                    'name':       corp_data['name_{}'.format(n)],
                    'badge_name': corp_data['badge_name_{}'.format(n)],
                    'document':   corp_data['document_{}'.format(n)],
                    'email':      corp_data['email_{}'.format(n)]
                })

        if '' in corp_data:
            del corp_data['']

        del corp_data['_boleto_emitido']
        del corp_data['_nf_emitida']
        del corp_data['_details']

        print "adding corporate: ", corp_data['name']
        owner = get_or_add_account({
            'name': corp_data['incharge_name'],
            'email': corp_data['incharge_email'],
            'document': '00000000000'
        })
        corporate = corporate_service.create(corp_data, owner)
        for e in employees:
            corporate.add_people(corporate.id, e, owner)

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
