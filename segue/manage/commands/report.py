# -*- coding: utf-8 -*-
import sys, codecs, os
import itertools as it
import requests
import datetime
import tablib
import json
import yaml
import xmltodict
import dateutil.parser

from unidecode import unidecode
from pycorreios import Correios
from segue.models import *
from segue.core import db
from segue.hasher import Hasher
from support import *;

c = Correios()
ds = tablib.Dataset()
cache_file = './states.cache'

f_cache_content = codecs.open(cache_file, 'w+')
if os.path.getsize(cache_file) == 0:
    states_cache = {}
else:
    states_cache = json.load(f_cache_content)

def caravan_report(out_file = "caravan_report"):
    filename = out_file + "_" + str(datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")) + ".xls"
    print "generating report " + filename
    f = codecs.open('./' + filename,'w')
    ds.headers = ["NOME DA CARAVANA", "NOME DO LIDER", "EMAIL DO LIDER", "CIDADE", "ESTADO"]

    class fakeBuyer(object):
        def __init__(self, city):
            self.address_zipcode = 'NONEXISTENT'
            self.address_city = city

    for caravan in Caravan.query.all():
        buyer = fakeBuyer(caravan.city)

        data_list = [
            caravan.name,
            caravan.owner.name,
            caravan.owner.email,
            caravan.city,
            guess_state(buyer)
        ]
        ds.append(data_list)

    print "fechando arquivo..."
    f.write(ds.xls)
    f.close()

    print "done!"


def adempiere_format(out_file = "adempiere_export"):
    buyers_report(out_file, adempiere=True, testing=False)

def buyers_report(out_file = "buyers_report", adempiere=False, testing=False):
    counter = 0
    extension = ".txt" if adempiere else ".xls"

    filename = out_file + "_" + str(datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")) + extension
    print "generating report " + filename
    f = codecs.open('./' + filename,'w', 'utf-8')
    if adempiere:
        ds = []
    else:
        ds.headers = ["CODIGO DA INSCRICAO","EMAIL","NOME","TELEFONE","DOCUMENTO","ENDERECO","NUMERO","COMPLEMENTO","CIDADE","CEP","ESTADO","TIPO DE INSCRICAO","FORMA DE PAGAMENTO","VALOR","DATA DO PAGAMENTO","NOSSO NUMERO"]

    for account in Account.query.all():
        if testing:
            counter += 1
            if counter > 100:
                break

        purchases = account.purchases
        buyers      = [ p.buyer for p in purchases ]
        payments    = list(it.chain.from_iterable([ p.payments for p in purchases ]))
        #transitions = list(it.chain.from_iterable([ p.transitions for p in payments ]))

        if not purchases: continue

        for p in purchases:
            if p.status == 'paid':
                purchase = p
                buyer = purchase.buyer
                if not buyer:
                    continue
                guessed_state = guess_state(buyer)
                ongoing_payments = [ payment for payment in p.payments if (payment.status in Payment.VALID_PAYMENT_STATUSES) ]
                if ongoing_payments:
                    payment = ongoing_payments[0]

                data_list = [
                    purchase.id,
                    account.email,
                    account.name,
                    account.phone,
                    account.document,
                    buyer.address_street,
                    buyer.address_number,
                    buyer.address_extra,
                    buyer.address_city,
                    buyer.address_zipcode,
                    guessed_state,
                    get_category(purchase.product.category),
                    payment.type,
                    purchase.product.price,
                    get_transition_date(payment),
                    get_our_number(payment)
                ]

                ds.append(data_list)

    print "fechando arquivo..."
    if adempiere:
        f.write(adempiere_filter(ds))
    else:
        f.write(ds.xls)
    f.close()

    print "escrevendo arquivo states_cache..."
    json.dump(states_cache, f_cache_content)
    f_cache_content.close()
    print "done!"

def adempiere_filter(data):
    content = u""
    s = "þ"
    # ["0CODIGO DA INSCRICAO","1EMAIL","2NOME",
    #  "3TELEFONE","4DOCUMENTO","5ENDERECO","6NUMERO",
    #  "7COMPLEMENTO","8CIDADE","9CEP","10ESTADO","11TIPO DE INSCRICAO",
    #  "12FORMA DE PAGAMENTO","13VALOR","14DATA DO PAGAMENTO","15NOSSO NUMERO"]
    # separator: þ

    for d in data:
        purchase_id = d[0]
        cpf = format_document(d[4]) or "nulo"
        cnpj = "nulo"
        name = d[2]
        email = d[1]
        phone_1 = d[3] or "nulo"
        phone_2 = "nulo"
        zipcode = d[9] or "nulo"
        state = d[10] or "nulo"
        city = d[8] or "nulo"
        address = d[5]
        address_number = d[6] or "nulo"
        address_extra = d[7] or "nulo"
        #TODO: in the future, allow for multiple tickets in one single document.
        quantity = 1
        amount = d[13]
        ticket_type = d[11]

        content += u"{}þ{}þ{}þ{}þ{}þ{}þ{}þ{}þ{}þ{}þ{}þ{}þ{}þ{}þ{}þ{}þ{}þ{}þ{}\n".format(
            purchase_id, "PF", cpf, cnpj, name,
            email, phone_1, phone_2, zipcode, state, city, address, address_number,
            "nulo", address_extra, quantity, amount, "0", ticket_type)

    return content

def format_document(value, type="CPF"):
    if type == "CPF" and value:
        return "{}{}{}.{}{}{}.{}{}{}-{}{}".format(*list(value))
    else:
        return "nulo"

def get_transition_date(payment):
    transition = [ transition for transition in payment.transitions if (transition.new_status in Payment.VALID_PAYMENT_STATUSES) ][0]
    if payment.type == 'pagseguro':
        return get_date_pagseguro(transition)
    elif payment.type == 'boleto':
        if hasattr(transition, 'payment_date'):
            return transition.payment_date
        else:
            return transition.created
    else:
        return transition.created

def get_date_pagseguro(transition):
    pagseguro_data = xmltodict.parse(transition.payload)
    date = dateutil.parser.parse(pagseguro_data['transaction']['lastEventDate'])
    naive = date.replace(tzinfo=None)
    return naive

def guess_state(buyer):
    if buyer.address_zipcode in states_cache.keys():
        return states_cache[buyer.address_zipcode]
    else:
        result = c.cep(buyer.address_zipcode)
        if 'uf' in result:
            states_cache[buyer.address_zipcode] = result['uf']
            return result['uf']
        else:
            found = City.query.filter_by(name = strip_accents(buyer.address_city.upper())).all()
            if len(found):
                return found[0].state
            else:
                return ""

def strip_accents(item):
    return unidecode(item)

def get_category(name):
    if name == 'normal':
        return "Ingresso individual"
    elif name == 'student':
        return "Ingresso de estudante"
    elif name == 'caravan':
        return "Ingresso de caravana"
    elif name == 'corp':
        return "Ingresso corporativo"
    elif name == 'gov':
        return "Empenho"
    else:
        return "Tipo de ingresso desconhecido"

def get_our_number(payment):
    return payment.our_number if getattr(payment, 'our_number', None) is not None else ''
