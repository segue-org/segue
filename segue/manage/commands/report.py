# -*- coding: utf-8 -*-
import sys, codecs
import itertools as it
import requests
import datetime

from unidecode import unidecode
from segue.models import *
from segue.core import db
from colorama import init, Fore as F, Back as B
#init()
LINE = "\n"

def buyers_report(out_file = "buyers_report"):
    sys.stdout = codecs.open('./' + out_file + "_" + str(datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%s")) + ".csv",'w','utf-8')
    print u'"CODIGO DA INSCRICAO";"EMAIL";"NOME";"TELEFONE";"DOCUMENTO";"ENDERECO";"NUMERO";"COMPLEMENTO";"CIDADE";"CEP";"ESTADO";"TIPO DE INSCRICAO";"FORMA DE PAGAMENTO";"VALOR";"DATA DA COMPRA"'
    
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
                guessed_state = guess_state(buyer.address_city)
                ongoing_payments = [ payment for payment in p.payments if (payment.status in Payment.VALID_PAYMENT_STATUSES) ]
                if ongoing_payments:
                    payment = ongoing_payments[0]
                print u'"{1.id}";"{0.email}";"{0.name}";"{0.phone}";"{0.document}";"{2.address_street}";"{2.address_number}";"{2.address_extra}";"{2.address_city}";"{2.address_zipcode}";"{4}";"{5}";"{3.type}";{1.product.price};{6}'.format(account,purchase,buyer,payment,guessed_state,get_category(purchase.product.category),format_date(purchase.last_updated))

def guess_state(city_name):
  found = City.query.filter_by(name = stripe_accents(city_name.upper())).all()
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
  elif name == 'corp':
      return "Ingresso corporativo"
  elif name == 'gov':
      return "Empenho"
  else:
      return "Tipo de ingresso desconhecido"

def format_date(date):
  return date.strftime("%d/%m/%Y %H:%M:%S")