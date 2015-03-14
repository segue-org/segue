from segue.core import db
from segue.errors import NotAuthorized

from factories import BuyerFactory, PurchaseFactory, PaymentFactory, PagSeguroPaymentFactory
from .pagseguro import PagSeguroSessionFactory
from models import Purchase, Payment

import schema

class PurchaseFilterStrategies(object):
    def given(self, **criteria):
        result = []
        for key, value in criteria.items():
            method = getattr(self, "by_"+key)
            result.append(method(value))
        return result

    def by_customer_id(self, value):
        return Purchase.customer_id == value

class PurchaseService(object):
    def __init__(self, db_impl=None, payments=None, strategies=None):
        self.db = db_impl or db
        self.payments = payments or PaymentService()
        self.filter_strategies = strategies or PurchaseFilterStrategies()

    def query(self, by=None, **kw):
        kw['customer_id'] = by.id
        filter_list = self.filter_strategies.given(**kw)
        return Purchase.query.filter(*filter_list).all()

    def create(self, buyer_data, product, account):
        buyer    = BuyerFactory.from_json(buyer_data, schema.buyer)
        purchase = PurchaseFactory.create(buyer, product, account)
        self.db.session.add(purchase)
        self.db.session.commit()
        return purchase

    def get_one(self, purchase_id, by=None):
        purchase = Purchase.query.get(purchase_id)
        if not purchase: return None
        if not self.check_ownership(purchase, by): raise NotAuthorized()
        return purchase

    def check_ownership(self, purchase, alleged):
        return purchase and alleged and purchase.customer_id == alleged.id

    def create_payment(self, purchase_id, payment_method, payment_data, by=None):
        purchase = self.get_one(purchase_id, by=by)
        return payments.create(purchase, payment_method, payment_data)

class PaymentService(object):
    def __init__(self, **services):
        self.services = services

    def create(self, purchase, method, data):
        if method not in self.services:
            return NotImplementedError(method+' is not a valid payment method')
        return self.services[method].create(purchase, data)

    def get_one(self, purchase_id, payment_id):
        result = Payment.query.filter(Purchase.id == purchase_id, Payment.id == payment_id)
        return result.first()

    def notify(self, purchase_id, payment_id, notification_code):
        pass

class PagSeguroPaymentService(object):
    def __init__(self, session_factory=None):
        self.session_factory = session_factory or PagSeguroSessionFactory()

    def create(self, purchase, data={}):
        # TODO: collect all other valid payments to allow the calculation of outstanding amount
        payment = PagSeguroPaymentFactory.create(purchase)
        db.session.add(payment)
        db.session.commit()

        session = self.session_factory.create_session()
        session.shipping = None
        session.reference_prefix = "SEGUE-FISL16-"
        session.reference = "{0}-PA{1:05d}".format(payment.reference, payment.id)
        session.items = [ dict(
            id="0001", description="ingresso fisl16", amount=payment.amount, quantity=1, weight=0
        ) ]
        session.checkout()
        return payment



