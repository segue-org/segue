# -*- coding: utf-8 -*-
import codecs, os
import datetime
import tablib
import json
import yaml

from segue.core import db
from segue.hasher import Hasher
from segue.models import *
from segue.product.services import ProductService
from segue.caravan.services import CaravanService, CaravanInviteService
from segue.account.services import AccountService
from segue.purchase.services import PurchaseService
from segue.purchase.boleto.models import BoletoPayment, BoletoTransition

ds = tablib.Dataset()

product_service = ProductService()
caravan_service = CaravanService()
caravan_invite_service = CaravanInviteService()
account_service = AccountService()
purchase_service = PurchaseService()

def import_caravan(in_file, caravan_yaml):
    caravan_data = yaml.load(open(caravan_yaml))
    product = product_service.get_product(caravan_data['product_id'])
    our_number = caravan_data['our_number']
    payment_date = caravan_data['payment_date']
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
            print "lider da caravana:", item['NOME'], item['EMAIL']
            first = False
            has_caravan = True
            leader_purchase = CaravanLeaderPurchase.query.filter(
                                CaravanLeaderPurchase.caravan == caravan and
                                CaravanLeaderPurchase.customer.email == item['EMAIL']
                              ).first()
            if not leader_purchase:
                purchase = add_leader_purchase(caravan, product, item, our_number, payment_date)
            else:
                purchase = leader_purchase
        else:
            if has_caravan:
                account = add_account(item)
                print "convidado da caravana: ", account.email
                add_caravan_rider(caravan, account)
                add_rider_purchase_and_payment(product, account, caravan, purchase.buyer, our_number, payment_date)

    print "####################### DONE! #############################"

def get_caravan(item, caravan_data):
    is_owner_registered = account_service.is_email_registered(item['EMAIL'])
    if is_owner_registered:
        caravan_owner = Account.query.filter(Account.email == item['EMAIL']).one()
        caravan = Caravan.query.filter(Caravan.owner_id == caravan_owner.id).first()
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

    invite_data = {
        'hash': h.generate(),
        'recipient': account.email,
        'name': account.name,
        'status': 'accepted'
    }

    invite = caravan_invite_service.create(caravan.id, invite_data, by=caravan.owner, send_email=False)

def add_leader_purchase(caravan, product, owner_data, our_number, payment_date):
    # creates fake purchase for the caravan leader
    buyer_data = {
        'kind': 'person',
        'name': owner_data['NOME'],
        'document': owner_data['CPF'],
        'contact': owner_data['NOME'],
        'address_street': owner_data['ENDERECO'],
        'address_number': owner_data['NUMERO'],
        'address_city': owner_data['CIDADE'],
        'address_country': 'BRASIL',
        'address_zipcode': owner_data['CEP']
    }

    purchase = purchase_service.create(buyer_data, product, caravan.owner)
    purchase.kind = 'caravan-leader'
    purchase.caravan = caravan
    purchase.status = 'paid'
    db.session.add(purchase)

    payment_data = {
        'type': 'boleto',
        'purchase_id': purchase.id,
        'status': 'paid',
        'amount': product.price,
        'our_number': our_number
    }
    leader_payment = BoletoPayment(**payment_data)

    transition_data = {
        'old_status': 'pending',
        'new_status': 'paid',
        'source': 'script',
        'payment': leader_payment,
        'payment_date': payment_date,
        'paid_amount' : product.price
    }
    transition = BoletoTransition(**transition_data)

    db.session.add(leader_payment)
    db.session.add(transition)
    db.session.commit()

    return purchase

def add_rider_purchase_and_payment(product, account, caravan, buyer, our_number, payment_date):
    # create fake purchase/payment for the caravan rider (account)

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

    payment_data = {
        'type': 'boleto',
        'purchase_id': rider_purchase.id,
        'status': 'paid',
        'amount': product.price,
        'our_number': our_number
    }
    rider_payment = BoletoPayment(**payment_data)

    transition_data = {
        'old_status': 'pending',
        'new_status': 'paid',
        'source': 'script',
        'payment': rider_payment,
        'payment_date': payment_date,
        'paid_amount' : product.price
    }
    transition = BoletoTransition(**transition_data)

    db.session.add(rider_payment)
    db.session.add(transition)
    db.session.commit()

def add_caravan(caravan_data, account):
    data = {
        'name': caravan_data['caravan_name'],
        'city': caravan_data['caravan_city'],
        'description': caravan_data['caravan_description']
    }
    return caravan_service.create(data, account)

def add_account(item):
    account_data = {
        'role': 'user',
        'name': item['NOME'],
        'email': item['EMAIL'],
        'document': str(item['CPF']).translate(None, './-'),
        'country': 'BRASIL',
        'state': item['ESTADO'],
        'city': item['CIDADE'],
        'phone': item['TELEFONE'],
        'password': generate_password()
    }

    if account_service.is_email_registered(account_data['email']):
        return Account.query.filter(Account.email == account_data['email']).one()
    else:
        return account_service.create(account_data)

def generate_password():
    h = Hasher(10)
    return h.generate()
