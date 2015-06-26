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
from segue.mailer import MailerService

ds = tablib.Dataset()

product_service = ProductService()
caravan_service = CaravanService()
caravan_invite_service = CaravanInviteService()
account_service = AccountService()
purchase_service = PurchaseService()
mailer_service = MailerService()

def import_avulsos(in_file):
    with open(in_file, "r") as f:
        ds.csv = f.read()

    counter = 0
    for item in ds.dict:
        # dados do comprador
        buyer_data = {
            'kind': 'person',
            'name': item['NOME'],
            'document': item['CPF'],
            'contact': item['NOME'],
            'address_city': item['CIDADE'],
            'address_street': item['ENDERECO'],
            'address_number': item['NUMERO'],
            'address_zipcode': item['CEP'],
            'address_country': "BRASIL"
        }

        if item['COMPLEMENTO']:
            buyer_data.update( {'address_extra': item['COMPLEMENTO']} )

        print "####################"
        print "buyer data: ", buyer_data

        # efetuando purchase
        product = get_product(item['Categoria'], item['Valor'])
        if not product:
            print "product not found: ", item['Categoria'], item['Valor']
            break
        else:
            print "product: ", product.category, product.price

        print "searching for email: ", item['EMAIL']
        owner = Account.query.filter(Account.email == item['EMAIL'].strip()).first()

        if item['caravan_id']:
            caravan = Caravan.query.filter(Caravan.id == item['caravan_id']).first()

        if owner:
            print "found owner: ", owner.name, owner.email
        else:
            #create owner Account
            account_data = {
                'email': item['EMAIL'],
                'name': item['NOME'],
                'password': generate_password(),
                'cpf': item['CPF'],
                'country': "BRASIL",
                'city': item['CIDADE'],
                'phone': item['TELEFONE']
            }
            print "owner not found, creating: ", account_data
            owner = account_service.create(account_data)

        if not owner:
            print "error in owner, could not create"
            break

        purchase = purchase_service.create(buyer_data, product, owner)

        if item['caravan_id'] and item['Categoria'] == 'caravan':
            purchase.kind = 'caravan-rider'
            purchase.caravan = caravan
        else:
            purchase.kind = 'single'

        purchase.status = 'paid'

        # dados do payment
        payment_data = {
            'type': 'boleto',
            'purchase': purchase,
            'status': 'paid',
            'amount': product.price,
            'our_number': item['Nosso Numero'],
        }

        payment = BoletoPayment(**payment_data)

        transition_data = {
            'old_status': 'pending',
            'new_status': 'paid',
            'source': 'script',
            'payment': payment,
            'payment_date': format_date(item['Data do pagamento']),
            'paid_amount' : product.price
        }
        transition = BoletoTransition(**transition_data)

        db.session.add(purchase)
        db.session.add(payment)
        db.session.add(transition)
        db.session.commit()

        if item['caravan_id'] and item['Categoria'] == 'caravan':
            caravan_service.update_leader_exemption(caravan.id, caravan.owner)

        mailer_service.notify_payment(purchase, payment)

        counter += 1

    print "###########################################################"
    print "records processed: ", counter
    print "####################### DONE! #############################"

def format_date(date):
    items = date.split("/")
    return datetime.date(int(items[2]), int(items[1]), int(items[0]))

def get_product(category, price):
    return Product.query.filter(Product.category == category and Product.price == price).first()

def generate_password():
    h = Hasher(8)
    return h.generate()
