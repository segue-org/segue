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

c = Correios()
ds = tablib.Dataset()
cache_file = './states.cache'

f_cache_content = codecs.open(cache_file, 'w+')
if os.path.getsize(cache_file) == 0:
    states_cache = {}
else:
    states_cache = json.load(f_cache_content)

def import_caravan(in_file, caravan_yaml):
    caravan_data = yaml.load(open(caravan_yaml))
    product = Product.query.get(caravan_data['product_id'])
    print "################## IMPORTAR CARAVANA #######################"
    print "Caravana:", caravan_data['caravan_name']
    print "Produto:", product.description, product.price

    with open(in_file, "r") as f:
        ds.csv = f.read()

    first = True
    has_caravan = False
    for item in ds.dict:
        if first:
            caravan_id = get_caravan(item, caravan_data)
            caravan = Caravan.query.get(caravan_id)
            owner_data = item.copy()
            print "lider da caravana:", owner_data['NOME'], owner_data['EMAIL']
            first = False
            has_caravan = True
            buyer = add_buyer(caravan, item, product)
        else:
            if has_caravan:
                account = add_account(item)
                print "convidado da caravana: ", account.email
                add_caravan_rider(caravan, account)
                add_purchase(product, account, caravan, buyer)

    print "####################### DONE! #############################"

def get_caravan(item, caravan_data):
    caravan_owner = Account.query.filter(Account.email == item['EMAIL']).one()
    if caravan_owner:
        caravan = Caravan.query.filter(Caravan.owner_id == caravan_owner.id).one()
        if caravan:
            return caravan.id
        else:
            caravan = add_caravan(caravan_data, caravan_owner)
    else:
        account = add_account(item)
        caravan = add_caravan(caravan_data, account)

    return caravan.id

def add_caravan_rider(caravan, account):
    h = Hasher()
    invite = CaravanInvite.query.filter(CaravanInvite.caravan == caravan and CaravanInvite.recipient == account.email).first()
    if not invite:
        invite_data = {
            'hash': h.generate(),
            'caravan_id': caravan.id,
            'recipient': account.email,
            'name': account.name,
            'status': 'accepted'
        }
        invite = CaravanInvite(**invite_data)
        db.session.add(invite)
        db.session.commit()

def add_buyer(caravan, owner_data, product):
    # create a buyer and a purchase from the owner data
    buyer_data = {
        'kind': 'person',
        'name': owner_data['NOME'],
        'document': str(owner_data['CPF']).translate(None, './-'),
        'contact': owner_data['NOME'],
        'address_street': owner_data['ENDERECO'],
        'address_number': owner_data['NUMERO'],
        'address_extra': owner_data['COMPLEMENTO'],
        'address_zipcode': owner_data['CEP'],
        'address_city': owner_data['CIDADE'],
        'address_country': 'BRASIL'
    }
    buyer = Buyer(**buyer_data)
    db.session.add(buyer)
    db.session.flush()
    db.session.refresh(buyer)

    # create a purchase based on that buyer for the owner
    purchase_data = {
        'product_id': product.id,
        'customer_id': caravan.owner_id,
        'buyer_id': buyer.id,
        'status': 'paid',
        'caravan_id': caravan.id
    }
    owner_purchase = CaravanLeaderPurchase(**purchase_data)
    db.session.add(owner_purchase)
    db.session.commit()
    return buyer

def add_purchase(product, account, caravan, buyer):
    # create one purchase for the caravan rider (account)
    purchase_data = {
        'product_id': product.id,
        'customer_id': account.id,
        'buyer_id': buyer.id,
        'status': 'paid',
        'caravan_id': caravan.id
    }
    rider_purchase = CaravanRiderPurchase(**purchase_data)
    db.session.add(rider_purchase)
    db.session.commit()
    return rider_purchase


def add_caravan(caravan_data, account):
    caravan = Caravan(**caravan_data)
    caravan.owner_id = account.id
    db.session.add(caravan)
    db.session.flush()
    db.session.refresh(caravan)
    return caravan

def add_account(item):
    account = Account.query.filter(Account.email == item['EMAIL']).first()
    if not account:
        account_data = {
            'name': item['NOME'],
            'email': item['EMAIL'],
            'document': str(item['CPF']).translate(None, './-'),
            'state': item['ESTADO'],
            'city': item['CIDADE'],
            'phone': item['TELEFONE'],
            'password': generate_password()
        }
        account = Account(**account_data)
        db.session.add(account)
        db.session.flush()
        db.session.refresh(account)

    return account

def generate_password():
    h = Hasher(10)
    return h.generate()

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
    ds.headers = ["CODIGO DA INSCRICAO","EMAIL","NOME","TELEFONE","DOCUMENTO","ENDERECO","NUMERO","COMPLEMENTO","CIDADE","CEP","ESTADO","TIPO DE INSCRICAO","FORMA DE PAGAMENTO","VALOR","DATA DO PAGAMENTO","NOSSO NUMERO"]

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
                    get_transition_data(payment),
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

def get_transition_data(payment):
    if payment.type == 'pagseguro':
        transition = [ transition for transition in payment.transitions if (transition.new_status in Payment.VALID_PAYMENT_STATUSES) ]
        transition = transition[0]
        return get_date_pagseguro(transition)
    else:
        transition = payment.most_recent_transition
        return transition.payment_date

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
