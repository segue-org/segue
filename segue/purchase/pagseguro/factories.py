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
        payment = PaymentFactory.create(cls.model, purchase)
        payment.reference = "A{0:05d}-PU{1:05d}".format(purchase.customer.id, purchase.id)
        return payment

class PagSeguroSessionFactory(object):
    def __init__(self, use_env=None):
        self.use_env = use_env or config.PAGSEGURO_ENV
        if not self.use_env: raise(BadConfiguration('No env set for pagseguro'))

    def create_session(self, payment):
        # TODO: make the use of ConfigSandbox configurable
        pg = PagSeguro(config.PAGSEGURO_EMAIL, config.PAGSEGURO_TOKEN)
        pg.config = ConfigSandbox

        buyer = payment.purchase.buyer
        product = payment.product
        pg.shipping = {
            'type':        pg.NONE,
            "street":      buyer.address_street,
            "number":      buyer.address_number,
            "complement":  buyer.address_extra,
            "postal_code": buyer.address_zipcode,
            'city':        buyer.address_city,
            "country":     buyer.address_country
        }
        pg.reference_prefix = "SEGUE-FISL16-"
        pg.reference = "{0}-PA{1:05d}".format(payment.reference, payment.id)
        amount = "{0:0.2f}".format(payment.amount)

        pg.items = [ dict(
            id="0001", description=product.description, amount=amount, quantity=1, weight=0
        ) ]
        return pg
