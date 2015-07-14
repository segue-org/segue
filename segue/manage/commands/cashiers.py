# coding: utf-8

import codecs
import sys
import odswriter as ods

from decimal import Decimal
from inflection import parameterize
from datetime import datetime

from segue.core import config

from segue.purchase.cash import CashPaymentService
from segue.account.services import AccountService
from segue.frontdesk.models import Person

from support import *;

USAGE = """
    python manage.py cashiers --cashier_ids=id1,id2,id3
"""

DATE_FORMAT = "%Y-%m-%d"

def cashiers(cashier_ids=None):
    if not cashier_ids: print USAGE; return

    init_command()

    accounts = AccountService()
    cash = CashPaymentService()

    dates = [ datetime.strptime(d,DATE_FORMAT) for d in config.EVENT_DATES ]
    cashiers = [ accounts.get_one(c,check_ownership=False) for c in cashier_ids.split(",") ]

    for cashier in cashiers:
        filename = "report_{}.ods".format(parameterize(cashier.name))
        with ods.writer(open(filename,"wb")) as odsfile:
            for date in dates:
                sheet = odsfile.new_sheet(date.strftime("dia %d"))
                sheet.writerow(["hora","modo","valor","id","nome","produto"])
                report = cash.for_cashier(cashier, date)

                for payment in report:
                    person = Person(payment.purchase)
                    for transition in payment.transitions:
                        row =  [
                            transition.created.time(), transition.mode, Decimal(payment.amount),
                            person.id, person.name, person.product.description
                        ]
                        sheet.writerow(row)

                summer = lambda f: sum([ x.amount for x in filter(f, report) ])

                sheet.writerow([None, u"total cartão",   summer(lambda p: p.mode == 'card') ])
                sheet.writerow([None, u"total dinheiro", summer(lambda p: p.mode == 'cash') ])
                sheet.writerow([None, u"total geral",    summer(lambda p: True            ) ])
