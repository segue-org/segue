import os.path

from segue.errors import NotAuthorized
from segue.core import config, db

from factories import CashPaymentFactory

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
        # TODO: actually moves payment status
        pass
