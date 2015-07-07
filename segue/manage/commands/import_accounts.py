# -*- coding: utf-8 -*-
import codecs, os
import datetime
import tablib
import json
import yaml

from segue.core import db
from segue.hasher import Hasher
from segue.models import *
from segue.mailer import MailerService
from segue.account.services import AccountService

ds = tablib.Dataset()

account_service = AccountService()
mailer_service = MailerService()

def import_accounts(in_file, product_id):
    with open(in_file, "r") as f:
        ds.csv = f.read()

        product = Product.query.get(product_id)

        for line in ds.dict:
            if not account_service.is_email_registered(line['email']):
                account_data = {
                    'name':     line['nome'],
                    'document': line['cpf'],
                    'email':    line['email'],
                    'password': generate_password()
                }
                account = Account(**account_data)
                db.session.add(account)
            else:
                account = Account.query.filter(Account.email == line['email']).first()


            if not account.has_valid_purchases:
                purchase_data = {
                    'product': product,
                    'customer': account,
                    'status': 'paid',
                    'kind': 'exempt'
                }

                purchase = Purchase(**purchase_data)
                db.session.add(purchase)
            else:
                purchase = account.identifier_purchase

            try:
                db.session.commit()
            except Exception, e:
                print e.__dict__

def generate_password():
    h = Hasher(8)
    return h.generate()
