import os.path
from datetime import date

from models import CashPayment
from ..factories import PaymentFactory

class CashPaymentFactory(PaymentFactory):
    model = CashPayment

    def create(self, purchase):
        payment = super(CashPaymentFactory, self).create(purchase, target_model=self.model)
        return payment
