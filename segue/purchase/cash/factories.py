import os.path
from datetime import date

from models import CashPayment, CashTransition
from ..factories import PaymentFactory, TransitionFactory
from ..errors import InvalidPaymentNotification

class CashPaymentFactory(PaymentFactory):
    model = CashPayment

    def create(self, purchase):
        payment = super(CashPaymentFactory, self).create(purchase, target_model=self.model)
        return payment

class CashTransitionFactory(TransitionFactory):
    model = CashTransition

    @classmethod
    def create(cls, payment, payload, source):
        mode       = payload.get('mode', None)
        cashier    = payload.get('cashier', None)
        ip_address = payload.get('ip_address', None)

        if not mode or not cashier or not ip_address: raise InvalidPaymentNotification()
        if not cashier.can_receive_money: raise InvalidPaymentNotification()

        transition = TransitionFactory.create(payment, source, target_model=cls.model)
        transition.mode       = mode
        transition.cashier    = cashier
        transition.ip_address = ip_address
        transition.new_status = 'paid'
        transition

        return transition
