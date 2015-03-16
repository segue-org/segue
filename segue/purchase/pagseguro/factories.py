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
        purchase = payment.purchase
        buyer    = purchase.buyer
        product  = purchase.product
        customer = purchase.customer

        pg = PagSeguro(config.PAGSEGURO_EMAIL, config.PAGSEGURO_TOKEN)
        pg.config = ConfigSandbox
        pg.sender = {
            "name":      buyer.name,
            "area_code": customer.phone[0:2].strip(),
            "phone":     customer.phone[2:].strip(),
            "email":     customer.email
        }
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

        pg.redirect_url     = '{}/api/purchases/{}/payment/{}/conclude'.format(config.BACKEND_URL, purchase.id, payment.id)
        pg.notification_url = '{}/api/purchases/{}/payment/{}/notify'.  format(config.BACKEND_URL, purchase.id, payment.id)

        pg.add_item(
            id="0001",
            description=product.description,
            amount="{0:0.2f}".format(payment.amount),
            quantity=1,
            weight=0
        )
        return pg
