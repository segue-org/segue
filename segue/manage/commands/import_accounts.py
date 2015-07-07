# -*- coding: utf-8 -*-
import codecs, os
import datetime
import tablib
import json
import yaml


from segue.core import db
from segue.hasher import Hasher
from segue.models import *
from segue.account.services import AccountService

from support import *

ds = tablib.Dataset()


def import_accounts(in_file, product_id, commit=False):
    init_command()
    accounts = AccountService()
    hasher = Hasher(8)

    skipped = 0
    created = 0

    with open(in_file, "r") as f:
        ds.csv = f.read()

        product = Product.query.get(product_id)

        for line in ds.dict:
            name     = line['nome']
            email    = line['email']
            document = line['cpf']
            password = hasher.generate()

            print "scanning {}{}{}...".format(F.RED, email, F.RESET)

            if accounts.is_email_registered(line['email']):
                print "... {}had account already!{}".format(F.RED, F.RESET)
                account = accounts.get_by_email(email)
            else:
                print "... {}creating account{}".format(F.GREEN, F.RESET)
                account = Account(name=name, email=email, document=document)
                db.session.add(account)

            if account.has_valid_purchases:
                print "... {}had purchase already!{}".format(F.RED, F.RESET)
                purchase = account.identifier_purchase
                skipped += 1
                continue
            else:
                print "... {}creating purchase{}".format(F.GREEN, F.RESET)
                purchase = Purchase(customer=account, product=product)
                purchase.kind   = 'exempt'
                purchase.status = 'paid'
                db.session.add(purchase)
                created += 1

        try:
            print "results: skipped={}, created={}".format(skipped, created)
            if commit:
                print "comitting!"
                db.session.commit()
            else:
                print "rolling back"
                db.session.rollback()
        except Exception, e:
            import traceback
            traceback.print_exc()
