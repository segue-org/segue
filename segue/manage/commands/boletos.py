# coding: utf-8

import codecs
import sys


from segue.purchase import PaymentService
from segue.purchase.boleto import BoletoPaymentService
from segue.purchase.boleto.parsers  import BoletoFileParser

from support import *;

def process_boletos(filename):
    init_command()
    content = open(filename, 'r').read()

    boleto_service = BoletoPaymentService()
    payment_service = PaymentService()
    parser = BoletoFileParser()

    good_payments = []
    late_payments = []
    bad_payments = []
    unknown_payments = []

    for entry in parser.parse(content):
        print F.RESET  + LINE
        print F.YELLOW + entry['line']

        payment = boleto_service.get_by_our_number(entry.get('our_number'))

        if not payment:
            print F.RED + "**** COULD NOT FIND PAYMENT FOR LINE: {line}".format(**entry)
            unknown_payments.append(entry)
            continue

        print F.RESET + "**** FOUND PAYMENT, applying transition"

        if entry['payment_date'] == payment.legal_due_date:
            print F.RED + "**** NEXT BUSINESS DAY PAYMENT TOLERATED ****"
        elif entry['payment_date'] > payment.legal_due_date:
            print F.RED + "**** LATE PAYMENT!!! ****"
            late_payments.append(dict(entry=entry, payment=payment))
            continue

        print F.RESET
        purchase, transition = payment_service.notify(payment.purchase.id, payment.id, entry, 'script')

        print F.YELLOW + "id={0.id} {0.old_status}->{0.new_status}\tR$ {0.paid_amount} ".format(transition)

        if transition.errors:
            print F.RED + "**** BAD TRANSITION! errors were: {0.errors}".format(transition)
            bad_payments.append(dict(entry=entry, payment=payment, errors=transition.errors))
            continue;
        else:
            print F.GREEN + "**** GOOD TRANSITION!"
            good_payments.append(dict(entry=entry, payment=payment))
            continue

    total_money = sum([ p['payment'].amount for p in good_payments])

    print F.GREEN + u"==============================================================="
    print F.GREEN + u"VALIDOS             {}".format(len(good_payments))
    print F.GREEN + u"ATRASADOS           {}".format(len(late_payments))
    print F.GREEN + u"ERRADOS             {}".format(len(bad_payments))
    print F.GREEN + u"NAO-RECONHECIDOS    {}".format(len(unknown_payments))
    print F.GREEN + u"RECEITA TOTAL    R$ {:.2f}".format(float(total_money))

    print F.YELLOW + u"***** PAGAMENTOS NAO-RECONHECIDOS *****"
    for entry in unknown_payments:
        print_entry(entry)

    print F.YELLOW + u"***** PAGAMENTOS ERRADOS *****"
    for case in bad_payments:
        print F.RED   + u"*****************************"
        print_payment(case['payment'])
        print_entry(case['entry'])
        print F.RED + "ERROR: {errors}".format(**case)
        print ""

    print F.YELLOW + u"***** PAGAMENTOS ATRASADOS *****"
    for case in late_payments:
        print F.RED   + u"*****************************"
        print_payment(case['payment'])
        print_entry(case['entry'])
        print F.RED + "ERROR: late payemnt"
        print ""

def print_entry(entry):
    print F.RESET + u"NOSSO NUMERO: {our_number}".format(**entry)
    print F.RESET + u"VALOR: R$ {amount:0.2f}".format(**entry)
    print F.RESET + u"DATA DE PAGAMENTO: {payment_date}".format(**entry)

def print_payment(payment):
    print F.RESET + u"NOME:  {0.purchase.customer.name}".format(payment)
    print F.RESET + u"EMAIL: {0.purchase.customer.email}".format(payment)
    print F.RESET + u"VALOR: R$ {0.amount:0.2f}".format(payment)
    print F.RESET + u"TELEFONE: {0.purchase.customer.phone}".format(payment)
    print F.RESET + u"PRODUTO: {0.purchase.product.description}".format(payment)
    print F.RESET + u"CATEGORIA: {0.purchase.product.category}".format(payment)
    print F.RESET + u"DATA DE VENC: {0.due_date}".format(payment)
