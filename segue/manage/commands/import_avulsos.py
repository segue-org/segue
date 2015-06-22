# -*- coding: utf-8 -*-
import codecs, os
import datetime
import tablib
import json
import yaml

from segue.core import db
from segue.hasher import Hasher
from segue.models import *
from segue.product import ProductService
from segue.caravan.services import CaravanService, CaravanInviteService
from segue.account.services import AccountService
from segue.purchase import PurchaseService

ds = tablib.Dataset()

product_service = ProductService()
caravan_service = CaravanService()
caravan_invite_service = CaravanInviteService()
account_service = AccountService()
purchase_service = PurchaseService()

def import_avulsos(in_file):
    with open(in_file, "r") as f:
        ds.csv = f.read()

    for item in ds.dict:
        # dados do comprador
        buyer_data = {
            'kind': 'person',
            'name': item['NOME'],
            'document': item['CPF'],
            'contact': item['NOME'],
            'address_street': item['ENDERECO'],
            'address_number': item['NUMERO'],
            'address_extra': item['COMPLEMENTO'],
            'address_zipcode': item['CEP'],
            'address_country': "BRASIL"
        }

        # efetuando purchase
        product = get_product(item['Categoria'], item['Valor'])
        caravan = caravan_service.get_one(item['caravan_id'])
        purchase = purchase_service.create(buyer_data, product, caravan.owner)
        purchase.kind = 'caravan-rider'
        purchase.caravan = caravan
        purchase.status = 'paid'
        db.session.add(purchase)

        # dados do payment
        payment_data = {
            'type': 'boleto',
            'purchase_id': purchase.id,
            'status': 'paid',
            'amount': product.price,
            'bo_our_number': item['Nosso Numero'],
        }

        rider_payment = Payment(**payment_data)

        db.session.add(rider_payment)
        db.session.commit()

        # TODO: inserir transition para "paid", contendo item["Data do pagamento"]


    print "####################### DONE! #############################"
