from requests.exceptions import RequestException
from segue.errors import ExternalServiceError
from segue.purchase.errors import InvalidPaymentNotification, NoSuchPayment
from segue.core import db, logger
from segue.hasher import Hasher

from .factories import PromoCodePaymentFactory, PromoCodeTransitionFactory
from .models import PromoCode

class PromoCodeService(object):
    def __init__(self, sessions=None, factory=None):
        self.hasher = Hasher(length=10, prefix="PC")

    def create(self, product, description=None, creator=None, discount=1, qty=1):
        for counter in xrange(qty):
            str_description = "{} - {}/{}".format(description, counter+1, qty)

            p = PromoCode()
            p.creator     = creator
            p.product     = product
            p.description = str_description
            p.hash_code   = self.hasher.generate()
            p.discount    = discount

            db.session.add(p)
            db.session.commit()

        return qty

    def check(self, hash_code):
        promocode = PromoCode.query.filter(PromoCode.hash_code == hash_code).first()
        if promocode:
            if promocode.used: return None
        return promocode

class PromoCodePaymentService(object):
    def __init__(self, sessions=None, factory=None):
        self.factory  = factory  or PromoCodePaymentFactory()

    def create(self, purchase, data=None):
        payment = self.factory.create(purchase)
        db.session.add(payment)
        db.session.commit()
        return payment

    def process(self, payment):
        pass

    def notify(self, purchase, payment, payload=None, source='notification'):
        pass
