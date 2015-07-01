import re

from segue.core import config, logger
from segue.hasher import Hasher
from segue.factory import Factory
from segue.purchase.factories import PaymentFactory, TransitionFactory
from segue.errors import BadConfiguration
from segue.purchase.errors import InvalidPaymentNotification

from models import PromoCode, PromoCodePayment, PromoCodeTransition

class PromoCodePaymentFactory(PaymentFactory):
    model = PromoCodePayment

    def __init__(self):
        pass

    def create(self, purchase, promocode):
        payment = super(PromoCodePaymentFactory, self).create(purchase, target_model=self.model)
        payment.promocode = promocode
        payment.amount    = purchase.product.price * promocode.discount
        if promocode.discount == 1:
            payment.status = 'paid'
        else:
            payment.status = 'confirmed'
        return payment

class PromoCodeTransitionFactory(TransitionFactory):
    model = PromoCodeTransition

    @classmethod
    def check_reference(cls, payment, reference):
        pass
        # reference_parts = re.findall(r'(\d{5})', reference)
        # if len(reference_parts) != 3: raise InvalidPaymentNotification('reference string is not valid!')
        #
        # account_id, purchase_id, payment_id = reference_parts
        # if int(payment_id)  != payment.id: raise InvalidPaymentNotification('payment id does not match!')
        # if int(purchase_id) != payment.purchase.id: raise InvalidPaymentNotification('purchase id does not match')
        # if int(account_id)  != payment.purchase.customer.id: raise InvalidPaymentNotification('account id does not match')

    @classmethod
    def create(cls, notification_code, payment, source):
        pass
        # logger.debug('received xml from pagseguro %s', xml_payload)
        # reference, status = cls.parse_xml_payload(payment, xml_payload)
        # cls.check_reference(payment, reference)
        #
        # transition = TransitionFactory.create(payment, source, target_model=cls.model)
        # transition.notification_code = notification_code
        # transition.new_status        = status
        # transition.payload           = xml_payload.decode('iso-8859-1')
        # return transition
