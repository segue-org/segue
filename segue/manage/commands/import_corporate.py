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
from segue.product.models import CorporateProduct, Product
from segue.corporate.services import CorporateService, EmployeeAccountService
from segue.corporate.models import DepositPayment, DepositTransition, GovPayment, GovTransition
from segue.account.services import AccountService
from segue.purchase.services import PurchaseService
from segue.purchase.boleto.models import BoletoPayment, BoletoTransition
from segue.purchase.pagseguro.models import PagSeguroPayment, PagSeguroTransition
from segue.mailer import MailerService

ds = tablib.Dataset()

corporate_service = CorporateService()
employee_service = EmployeeAccountService()
account_service = AccountService()
purchase_service = PurchaseService()
mailer_service = MailerService()

counter = 0
counter_added = 0

def import_corporate(in_file, file_type):
    if file_type not in ['business', 'government']:
        print "error: only [business] or [government] options are available"
        return False

    global counter, counter_added

    with open(in_file, "r") as f:
        ds.csv = f.read()

    counter = 0
    counter_added = 0
    for item in ds.dict:
        process_line_corporate(item, mode=file_type)

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

def process_line_corporate(item, mode="business"):
    if mode == 'business':
        paid_flag = '*pago'
        amount = item['amount']
    elif mode == 'government':
        paid_flag = '*nota_empenho'
        # amount paid isn't variable, because the price is fixed.
        amount = None

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

    remove_from_dict = {
        'government': [
            '_id', '_data_envio', '*nota_empenho', '_idioma_inicial', '_data_inicio',
            '_data_ultima_acao', '_issqn', '*participants', '_', 'description', '_details'

        ],
        'business': {
            '_id', '_data_envio', '*pago', '_issqn', '*participants', '_',
            '_boleto_emitido', '_nf_emitida', '_details',
            'payment_date', 'amount', 'our_number', 'description'
        },
    }

    counter += 1
    _details = None
    if item[paid_flag] == "SIM":
        status_purchase = 'paid'
    else:
        status_purchase = 'pending'
    # 16 -> number of employees slots in csv file
    for n in xrange(1, 17):
        if corp_data['name_{}'.format(n)] != '':
            employees.append({
                'name':         corp_data['name_{}'.format(n)],
                'badge_name':   corp_data['badge_name_{}'.format(n)],
                'document':     corp_data['document_{}'.format(n)],
                'email':        corp_data['email_{}'.format(n)],
                'organization': corp_data['name'],
            })

        del corp_data['name_{}'.format(n)]
        del corp_data['badge_name_{}'.format(n)]
        del corp_data['document_{}'.format(n)]
        del corp_data['email_{}'.format(n)]

    if '' in corp_data:
        del corp_data['']

    if mode == "business":
        _details = item['_details']

    print "adding corporate: ", corp_data['name']
    print "verifying owner of corporate: ", corp_data['incharge_email']

    if account_service.is_email_registered(corp_data['incharge_email']):
        owner = account_service.get_by_email(corp_data['incharge_email'])
    else:
        new_owner_data = {
            'email': corp_data['incharge_email'],
            'name': corp_data['incharge_name'],
            'password': generate_password(),
            'country': 'BRASIL',
            'city': corp_data['address_city'],
            'phone': corp_data['incharge_phone_1'],
        }
        owner = account_service.create(new_owner_data)

    # exclude purchase data from corp_data dict for insertion
    corp_data = clean_dict(corp_data, remove_from_dict[mode])

    # create corporate
    corporate = corporate_service.get_by_document(corp_data['document'])
    if not corporate:
        corporate = corporate_service.create(corp_data, owner)

    owner.corporate_id = corporate.id
    db.session.add(owner)

    for e in employees:
        print "trying to add person to corporate: ", e
        if account_service.is_email_registered(e['email']):
            account = account_service.get_by_email(e['email'])
            account.organization = e['name']
            account.badge_name = e['badge_name']
            account.corporate_id = corporate.id
            db.session.add(account)
            print "person found: ", e
        else:
            e['password'] = generate_password()
            e['country']  = 'BRASIL'
            e['city']     = corp_data['address_city']
            e['phone']    = corp_data['incharge_phone_1']
            print "person not found, trying to add: ", corporate, e, owner
            account = employee_service.create(corporate, e, owner)
            print "person not found, added: ", e, account
            account.corporate_id = corporate.id
            db.session.add(account)

        # add purchases and payments
        # def create(self, buyer_data, product, account, commit=True, **extra):
        corp_buyer_data = {
            'kind': 'company',
            'name': item['name'],
            'document': item['document'],
            'contact': item['incharge_email'],
            'address_street': item['address_street'],
            'address_number': item['address_number'],
            'address_extra': item['address_extra'],
            'address_zipcode': item['address_zipcode'],
            'address_city': item['address_city'],
            'address_country': 'BRASIL',
        }

        if amount and item['*participants']:
            product = find_corporate_product(item['*participants'], amount, mode)
            if product and not account.has_valid_corporate_purchases:
                corp_purchase = purchase_service.create(corp_buyer_data, product, account, corporate_id=corporate.id)
                print "purchase created for user: ", account.email

                # create payment for each employee
                if corp_purchase:
                    corp_payment_data = {
                        'purchase': corp_purchase,
                        'status': status_purchase,
                        'amount': product.price,
                        'description': format_description(item['description'], _details),
                    }

                    corp_transition_data = {
                        'old_status': status_purchase,
                        'new_status': status_purchase,
                        'source': 'import_corporate_' + mode,
                    }

                    if mode == "business":
                        if item['our_number']:
                            corp_payment_data.update({
                                'our_number': item['our_number']
                            })

                            if item[paid_flag] == "SIM":
                                try:
                                    payment_date = datetime.datetime.strptime(item['payment_date'], "%Y-%m-%d")
                                except ValueError:
                                    payment_date = None
                                corp_transition_data.update({
                                    'payment_date': payment_date
                                })

                            objPayment = BoletoPayment
                            objTransition = BoletoTransition
                        elif item['description'] == 'deposit':
                            objPayment = DepositPayment
                            objTransition = DepositTransition
                        elif item['description'] == 'pagseguro':
                            objPayment = PagSeguroPayment
                            objTransition = PagSeguroTransition
                    elif mode == "government":
                        # corp_payment_data.update({
                        #     'payment_date': datetime.datetime.strptime(item['_data_envio'], "%Y-%m-%d %H:%M:%S")
                        # })
                        objPayment = GovPayment
                        objTransition = GovTransition

                    corp_payment = objPayment(**corp_payment_data)
                    corp_transition_data.update({
                        'payment': corp_payment
                    })
                    corp_transition = objTransition(**corp_transition_data)
                    print "created corporate payment - type/id: ", corp_payment.__class__.__name__, corp_payment
                    print "created corporate transition - type/id: ", corp_transition.__class__.__name__, corp_transition

                corp_purchase.recalculate_status()
            else:
                print "product not found or account already have corporate purchase"
                return

            db.session.commit()

            print corp_data
            print "###################### employees: "
            print employees

        counter_added +=1

def find_corporate_product(participants, amount, mode):
    if mode == "business":
        print "amount, participants: ", amount, participants
        product_value = float(amount) / float(participants)
        print "value: ", product_value
        product = CorporateProduct.query.filter(CorporateProduct.price == product_value).first()
        return product if product else None
    elif mode == "government":
        # government is a unique product
        return Product.query.filter(Product.category == 'government').first()

def format_description(description, details):
    ret = description
    if details:
        if description:
            ret += u'/' + details
        else:
            ret += details
    return ret

def clean_dict(data, remove_list):
    for item in remove_list:
        del data[item]

    return data

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
