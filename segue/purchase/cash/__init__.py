import os.path
from datetime import timedelta

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

    def for_cashier(self, cashier, date):
        start_of_day = date.replace(hour=0,minute=0,second=0)
        end_of_day   = date.replace(hour=23,minute=59,second=59)
        of_this_cashier = CashTransition.cashier == cashier
        with_this_date  = CashTransition.created.between(start_of_day, end_of_day)
        query = CashPayment.query.join(CashTransition).filter(of_this_cashier, with_this_date)
        return query.all()
