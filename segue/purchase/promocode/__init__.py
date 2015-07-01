from requests.exceptions import RequestException
from segue.purchase.errors import InvalidPaymentNotification, NoSuchPayment, MustProvideDescription
from segue.core import db, logger
from segue.hasher import Hasher

from filters import PromoCodeFilterStrategies
from factories import PromoCodePaymentFactory, PromoCodeTransitionFactory
from models import PromoCode
from segue.purchase.cash import CashPaymentService

class PromoCodeService(object):
    def __init__(self, hasher=None, products=None, filters=None):
        self.hasher            = hasher  or Hasher(length=10, prefix="PC")
        self.filter_strategies = filters or PromoCodeFilterStrategies()

    def lookup(self, as_user=None, **kw):
        needle = kw.pop('q',None)
        limit  = kw.pop('limit',None)
        filter_list = self.filter_strategies.needle(needle, as_user, **kw)
        return PromoCode.query.filter(*filter_list).limit(limit).all()

    def query(self, **kw):
        base        = self.filter_strategies.joins_for(PromoCode.query, **kw)
        filter_list = self.filter_strategies.given(**kw)
        return base.filter(*filter_list).order_by(PromoCode.description).all()

    def create(self, product, description=None, creator=None, discount=100, quantity=1):
        if not description: raise MustProvideDescription()

        result = []
        for counter in xrange(quantity):
            str_description = "{} - {}/{}".format(description, counter+1, quantity)

            p = PromoCode()
            p.creator     = creator
            p.product     = product
            p.description = str_description
            p.hash_code   = self.hasher.generate()
            p.discount    = float(discount) / 100

            db.session.add(p)
            result.append(p)

        db.session.commit()
        return result

    def check(self, hash_code):
        logger.info("PromoCodeService.check, hash_code: %s", hash_code)
        promocode = PromoCode.query.filter(PromoCode.hash_code == hash_code).first()
        logger.info(promocode)
        if not promocode: return None
        if promocode.used: return None
        return promocode

class PromoCodePaymentService(object):
    def __init__(self, cash_service=None, promocodes=None, factory=None):
        self.factory  = factory  or PromoCodePaymentFactory()
        self.cash_service = cash_service or CashPaymentService()
        self.promocodes = promocodes or PromoCodeService()

    def create(self, purchase, data=dict()):
        hash_code = data.get('hash_code',None)
        if not hash_code: return InvalidHashCode()

        promocode = self.promocodes.check(hash_code)
        if not promocode: return InvalidHashCode()

        payment = self.factory.create(purchase, promocode)
        purchase.recalculate_status()

        db.session.add(purchase)
        db.session.add(payment)
        db.session.commit()
        return payment

    def process(self, payment):
        # the endpoint is the same of CashPaymentService
        return self.cash_service.process(payment)

    def notify(self, purchase, payment, payload=None, source='notification'):
        pass
