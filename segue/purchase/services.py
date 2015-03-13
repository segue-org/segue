from segue.core import db
from segue.errors import NotAuthorized

from factories import BuyerFactory, PurchaseFactory, PagSeguroSessionFactory
from models import Purchase, Payment

import schema

class PurchaseService(object):
    def create(self, buyer_data, product, account):
        buyer    = BuyerFactory.from_json(buyer_data, schema.buyer)
        purchase = PurchaseFactory.create(buyer, product, account)
        db.session.add(purchase)
        db.session.commit()
        return purchase

    def get_one(self, purchase_id, by=None):
        purchase = Purchase.query.get(purchase_id)
        if not self.check_ownership(purchase, by): raise NotAuthorized()
        return purchase

    def check_ownership(self, purchase, alleged):
        return purchase and alleged and purchase.customer_id == alleged.id

class PaymentService(object):
    def __init__(self, pagseguro=PagSeguroSessionFactory):
        pass

    def get_one(self, purchase_id, payment_id):
        result = Payment.query.filter(Purchase.id == purchase_id, Payment.id == payment_id)
        return result.first()

    def notify(self, purchase_id, payment_id, notification_code):
        pass

class PagSeguroPaymentService(object):
    def __init__(self, pagseguro=PagSeguroSessionFactory):
        pass



