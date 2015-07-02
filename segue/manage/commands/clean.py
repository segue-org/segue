import sys, codecs
import itertools as it

from segue.models import *
from segue.core import db

from support import *;

def clean_bad_buyers(start, end):
    init_command()
    sys.stdout = codecs.open('/dev/stdout','w','utf-8')
    start = int(start)
    end   = int(end)

    purchases_to_delete = []
    buyers_to_delete = []
    payments_to_delete = []

    for account in Account.query.filter(Account.id >= start, Account.id <= end).order_by(Account.id):

        purchases   = account.purchases
        buyers      = [ p.buyer for p in purchases ]
        payments    = list(it.chain.from_iterable([ p.payments for p in purchases ]))
        transitions = list(it.chain.from_iterable([ p.transitions for p in payments ]))

        if not purchases: continue
        print F.RESET + u"*************************"
        print F.RESET + u"ID={0.id}, NAME={0.name}, EMAIL={0.email}".format(account),

        has_errors = False
        looks_good = False
        for p in purchases:
            if p.status == 'paid':
                print F.GREEN + "purchase with id {} found. status is paid!".format(p.id)
                looks_good = True
                continue
            elif len(transitions):
                print F.GREEN + "there are {} transitions so we can suppose success?".format(len(transitions)),
                print F.YELLOW + ",".join([ t.new_status for t in transitions ])
                looks_good = True
                continue
            ongoing_payments = [ payment for payment in p.payments if getattr(payment,'code',None) ]
            if ongoing_payments:
                looks_good = True
                print F.GREEN + "found payment with valid ps_code on id {}. success?".format(ongoing_payments[0].id)
                continue;
            errors = figure_errors(p)
            has_errors = len(errors) > 0
            print F.RESET + u"\tID={0.id} BUYER={0.buyer.name}, with {1} payments".format(p, len(p.payments.all())),
            print F.RED   + "<---- {}".format(",".join(errors))
        if looks_good: continue

        if len(purchases) > 1:
            print F.RED + u"account has {} purchases {}".format(len(purchases), ",".join([ u"{}-{}".format(x.id,x.status) for x in purchases ]) )
            print F.YELLOW + "will delete {} purchases".format(len(purchases))
            purchases_to_delete.extend(purchases)
        if len(buyers) > 1:
            print F.RED + u"account has {} buyers    {}".format(len(buyers),    ",".join([ u"{}-{}".format(x.id,x.name)   for x in buyers    ]) )
            print F.YELLOW + "will delete {} buyers".format(len(buyers))
            buyers_to_delete.extend(buyers)
        if len(payments) > 1 and has_errors:
            print F.RED + u"account has {} payments  {}".format(len(payments),  ",".join([ u"{}-{}".format(x.id,x.status) for x in payments  ]) )
            print F.YELLOW + "will delete {} payments and {} purchases".format(len(payments), len(purchases))
            payments_to_delete.extend(payments)
            purchases_to_delete.extend(purchases)

    print "==================================="
    print "TOTAL OBJECTS IN ERROR (count may include repeats):"
    print "\t{} bad purchases".format(len(purchases_to_delete))
    print "\t{} bad buyers".format(len(buyers_to_delete))
    print "\t{} bad payments".format(len(payments_to_delete))

    print F.RED   + "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    print F.RED   + "deleting purchases...",
    for purchase in purchases_to_delete:
        db.session.delete(purchase)
    print F.GREEN + "done"
    print F.RED   + "deleting buyers...",
    for buyer in buyers_to_delete:
        db.session.delete(buyer)
    print F.GREEN + "done"
    print F.RED   + "deleting payments...",
    for payment in payments_to_delete:
        db.session.delete(payment)
    print F.GREEN + "done"

    db.session.rollback();
#    print F.BLACK + B.RED + "COMMITTING DELETIONS...",
#    db.session.commit()
#    print F.BLACK + B.GREEN + "DONE" + B.RESET


def figure_errors(purchase):
    errors = []
    name_parts = purchase.buyer.name.split(" ")
    if len(name_parts) < 2:
        errors.append("OnlyOneWord")
    elif len(name_parts) == 2 and any([ len(x) < 2 for x in name_parts ]):
        errors.append("OneNameTooShort")
    if not purchase.buyer:
        errors.append("BuyerNotPresent")
    elif len(purchase.buyer.address_extra or '') > 40:
        errors.append("AddressExtraTooLong")
    return errors

