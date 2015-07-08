import os.path

from segue.errors import NotAuthorized
from segue.core import config, db

from models import CashPayment, CashTransition
from factories import CashPaymentFactory, CashTransitionFactory

class CashPaymentService(object):
    def __init__(self, factory=None):
        self.factory = factory or CashPaymentFactory()

    def create(self, purchase, data=None):
        payment = self.factory.create(purchase)
        db.session.add(payment)
        db.session.commit()
        return payment

    def process(self, payment):
        url = "{}/#/purchase/{}/payment/{}/guide".format(config.FRONTEND_URL, payment.purchase.id, payment.id)
        return dict(redirectUserTo=url)

    def notify(self, purchase, payment, payload, source='notification'):
        return CashTransitionFactory.create(payment, payload, source)

    def for_cashier(self, cashier):
        return CashPayment.query.join(CashTransition).filter(CashTransition.cashier == cashier).all()
