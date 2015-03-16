from pagseguro import PagSeguro
from pagseguro.sandbox import ConfigSandbox

from segue.core import config
from segue.factory import Factory
from segue.purchase.factories import PaymentFactory
from segue.errors import BadConfiguration

from ..models import PagSeguroPayment

class PagSeguroPaymentFactory(Factory):
    model = PagSeguroPayment

    @classmethod
    def create(cls, purchase):
        payment = PaymentFactory.create(purchase, target_model=cls.model)
        payment.reference = "A{0:05d}-PU{1:05d}".format(purchase.customer.id, purchase.id)
        return payment

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
        return '{}/api/purchases/{}/payment/{}/conclude'.format(config.BACKEND_URL, purchase.id, payment.id)

    def notification_url(self, payment, purchase):
        return '{}/api/purchases/{}/payment/{}/notify'.format(config.BACKEND_URL, purchase.id, payment.id)

class PagSeguroSessionFactory(object):
    def __init__(self, use_env=None, details_factory=None):
        self.use_env = use_env or config.PAGSEGURO_ENV
        if not self.use_env: raise(BadConfiguration('No env set for pagseguro'))
        self.details_factory = details_factory or PagSeguroDetailsFactory()

    def create_session(self, payment):
        pg = PagSeguro(config.PAGSEGURO_EMAIL, config.PAGSEGURO_TOKEN)
        pg.config = ConfigSandbox

        pg.sender    = self.details_factory.create_sender(payment.purchase.customer, payment.purchase.buyer)
        pg.shipping  = self.details_factory.create_shipping(payment.purchase.buyer)
        pg.items     = [ self.details_factory.create_item(payment, payment.purchase.product) ]

        pg.reference_prefix = "SEGUE-FISL16-"
        pg.reference        = self.details_factory.reference(payment)
        pg.redirect_url     = self.details_factory.redirect_url(payment, payment.purchase)
        pg.notification_url = self.details_factory.notification_url(payment, payment.purchase)

        return pg
