# -*- coding: utf-8 -*-
import sys, codecs, os
import itertools as it
import requests
import datetime
import tablib
import json

from unidecode import unidecode
from pycorreios import Correios
from segue.models import *
from segue.core import db
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


def buyers_report(out_file = "buyers_report"):
    filename = out_file + "_" + str(datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")) + ".xls"
    print "generating report " + filename
    f = codecs.open('./' + filename,'w')
    ds.headers = ["CODIGO DA INSCRICAO","EMAIL","NOME","TELEFONE","DOCUMENTO","ENDERECO","NUMERO","COMPLEMENTO","CIDADE","CEP","ESTADO","TIPO DE INSCRICAO","FORMA DE PAGAMENTO","VALOR","DATA DA COMPRA","NOSSO NUMERO"]

    for account in Account.query.all():
        purchases = account.purchases
        buyers      = [ p.buyer for p in purchases ]
        payments    = list(it.chain.from_iterable([ p.payments for p in purchases ]))
        transitions = list(it.chain.from_iterable([ p.transitions for p in payments ]))

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
                    purchase.last_updated,
                    get_our_number(payment)
                ]
                ds.append(data_list)

    print "fechando arquivo..."
    f.write(ds.xls)
    f.close()

    print "escrevendo arquivo states_cache..."
    json.dump(states_cache, f_cache_content)
    f_cache_content.close()
    print "done!"

def guess_state(buyer):
    if buyer.address_zipcode in states_cache.keys():
        return states_cache[buyer.address_zipcode]
    else:
        result = c.cep(buyer.address_zipcode)
        if 'uf' in result:
            states_cache[buyer.address_zipcode] = result['uf']
            return result['uf']
        else:
            found = City.query.filter_by(name = stripe_accents(buyer.address_city.upper())).all()
            if len(found):
                return found[0].state
            else:
                return ""

def stripe_accents(item):
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
