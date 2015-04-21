# coding: utf-8

import codecs
import sys

sys.stdout = codecs.open("/dev/stdout", "w", "utf-8")

from segue.purchase import PaymentService
from segue.purchase.boleto import BoletoPaymentService
from segue.purchase.boleto.parsers  import BoletoFileParser

from colorama import init, Fore as F, Back as B
init()
LINE = "\n"

def process_boletos(filename):
    content = open(filename, 'r').read()

    boleto_service = BoletoPaymentService()
    payment_service = PaymentService()
    parser = BoletoFileParser()

    good_payments = []
    late_payments = []
    bad_payments = []

    for entry in parser.parse(content):
        print F.RESET  + LINE
        print F.YELLOW + entry['line']

        payment = boleto_service.get_by_our_number(entry.pop('our_number'))

        if not payment:
            print F.RED + "**** COULD NOT FIND PAYMENT FOR LINE: {line}".format(**entry)
            continue

        print F.RESET + "**** FOUND PAYMENT, applying transition"

        if entry['payment_date'] > payment.due_date:
            print F.RED + "**** LATE PAYMENT!!! ****"
            late_payments.append(dict(entry=entry, payment=payment))
            continue


        purchase, transition = payment_service.notify(payment.purchase.id, payment.id, entry, 'script')

        print F.YELLOW + "id={0.id} {0.old_status}->{0.new_status}\tR$ {0.paid_amount} ".format(transition)

        if transition.errors:
            print F.RED + "**** BAD TRANSITION! errors were: {0.errors}".format(transition)
            bad_payments.append(dict(entry=entry, payment=payment))
            continue;
        else:
            print F.GREEN + "**** GOOD TRANSITION!"
            good_payments.append(dict(entry=entry, payment=payment))
            continue

    total_money = sum([ p['payment'].amount for p in good_payments])

    print F.GREEN + u"==============================================================="
    print F.GREEN + u"valid payments {}".format(len(good_payments))
    print F.GREEN + u"late payments  {}".format(len(late_payments))
    print F.GREEN + u"bad payments   {}".format(len(bad_payments))
    print F.GREEN + u"total money R$ {:.2f}".format(float(total_money))

    for case in late_payments:
        print ""
        print F.RED   + u"*****************************"
        print F.RESET + u"NOME:  {payment.purchase.customer.name}".format(**case)
        print F.RESET + u"EMAIL: {payment.purchase.customer.email}".format(**case)
        print F.RESET + u"VALOR: R$ {payment.amount:0.2f}".format(**case)
        print F.RESET + u"TELEFONE: {payment.purchase.customer.phone}".format(**case)
        print F.RESET + u"PRODUTO: {payment.purchase.product.description}".format(**case)
        print F.RESET + u"CATEGORIA: {payment.purchase.product.category}".format(**case)
        print F.RESET + u"DATA DE VENC: {payment.due_date}".format(**case)
        print F.RESET + u"DATA DE PGTO: {entry[payment_date]}".format(**case)
