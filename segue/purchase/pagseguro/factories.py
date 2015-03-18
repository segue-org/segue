import re

from xml.etree import ElementTree
from pagseguro import PagSeguro
from pagseguro.sandbox import ConfigSandbox

from segue.core import config, logger
from segue.factory import Factory
from segue.purchase.factories import PaymentFactory, TransitionFactory
from segue.errors import BadConfiguration, InvalidPaymentNotification

from ..models import PagSeguroPayment, PagSeguroTransition

class PagSeguroPaymentFactory(Factory):
    model = PagSeguroPayment

    @classmethod
    def create(cls, purchase):
        payment = PaymentFactory.create(purchase, target_model=cls.model)
        payment.reference = "A{0:05d}-PU{1:05d}".format(purchase.customer.id, purchase.id)
        return payment

class PagSeguroTransitionFactory(TransitionFactory):
    model = PagSeguroTransition

    PAGSEGURO_STATUSES = {
        1: 'pending',  2: 'in analysis', 3: 'paid', 4: 'confirmed',
        5: 'disputed', 6: 'reimbursed',  7: 'cancelled'
    }

    @classmethod
    def parse_xml_payload(cls, payment, xml_payload):
        doc = ElementTree.fromstring(xml_payload)
        status_element    = doc.find('.//status')
        error_element     = doc.find('.//error')
        reference_element = doc.find('.//reference')

        if error_element:
            logger.error('pagseguro reported an error with our notification check: %s', error_element.text)
            raise InvalidPaymentNotification(error_element.text)

        if not status_element.text or not reference_element.text:
            logger.error('pagseguro reported a malformed response')
            raise InvalidPaymentNotification('malformed pagseguro response')

        resolved_status = cls.PAGSEGURO_STATUSES.get(int(status_element.text), 'unknown')
        return reference_element.text, resolved_status

    @classmethod
    def check_reference(cls, payment, reference):
        reference_parts = re.findall(r'(\d{5})', reference)
        if len(reference_parts) != 3: raise InvalidPaymentNotification('reference string is not valid!')

        account_id, purchase_id, payment_id = reference_parts
        if int(payment_id)  != payment.id: raise InvalidPaymentNotification('payment id does not match!')
        if int(purchase_id) != payment.purchase.id: raise InvalidPaymentNotification('purchase id does not match')
        if int(account_id)  != payment.purchase.customer.id: raise InvalidPaymentNotification('account id does not match')

    @classmethod
    def create(cls, notification_code, payment, xml_payload, source):
        logger.debug('received xml from pagseguro %s', xml_payload)
        reference, status = cls.parse_xml_payload(payment, xml_payload)
        cls.check_reference(payment, reference)

        transition = TransitionFactory.create(payment, source, target_model=cls.model)
        transition.notification_code = notification_code
        transition.new_status        = status
        transition.payload           = xml_payload
        return transition

class PagSeguroDetailsFactory(object):
    def create_sender(self, customer, buyer):
        return {
            "name":      buyer.name,
            "area_code": customer.phone[0:2].strip(),
            "phone":     customer.phone[2:].strip(),
            "email":     customer.email
        }

    def create_shipping(self, buyer):
        return {
            'type':        3,
            "street":      buyer.address_street,
            "number":      buyer.address_number,
            "complement":  buyer.address_extra,
            "postal_code": buyer.address_zipcode,
            'city':        buyer.address_city,
            "country":     buyer.address_country
        }

    def create_item(self, payment, product):
        return {
            "id":          "0001",
            "description": product.description,
            "amount":      "{0:0.2f}".format(payment.amount),
            "quantity":    1,
            "weight":      0
        }

    def reference(self, payment):
        return "{0}-PA{1:05d}".format(payment.reference, payment.id)

    def redirect_url(self, payment, purchase):
        return '{}/api/purchases/{}/payments/{}/conclude'.format(config.BACKEND_URL, purchase.id, payment.id)

    def notification_url(self, payment, purchase):
        return '{}/api/purchases/{}/payments/{}/notify'.format(config.BACKEND_URL, purchase.id, payment.id)

class PagSeguroSessionFactory(object):
    def __init__(self, use_env=None, details_factory=None):
        self.use_env = use_env or config.PAGSEGURO_ENV
        if not self.use_env: raise(BadConfiguration('No env set for pagseguro'))
        self.details_factory = details_factory or PagSeguroDetailsFactory()

    def notification_session(self, notification_code):
        pg = PagSeguro(config.PAGSEGURO_EMAIL, config.PAGSEGURO_TOKEN)
        if self.use_env != 'production': pg.config = ConfigSandbox
        pg.check = lambda: pg.check_notification(notification_code).xml
        return pg

    def payment_session(self, payment):
        pg = PagSeguro(config.PAGSEGURO_EMAIL, config.PAGSEGURO_TOKEN)
        if self.use_env != 'production': pg.config = ConfigSandbox

        pg.sender    = self.details_factory.create_sender(payment.purchase.customer, payment.purchase.buyer)
        pg.shipping  = self.details_factory.create_shipping(payment.purchase.buyer)
        pg.items     = [ self.details_factory.create_item(payment, payment.purchase.product) ]

        pg.reference_prefix = "SEGUE-FISL16-"
        pg.reference        = self.details_factory.reference(payment)
        pg.redirect_url     = self.details_factory.redirect_url(payment, payment.purchase)
        pg.notification_url = self.details_factory.notification_url(payment, payment.purchase)

        return pg
