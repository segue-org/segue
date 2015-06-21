from segue.core import db, logger

from segue.errors import NotAuthorized, NoSuchPayment, PurchaseAlreadySatisfied
from segue.product.errors import NoSuchProduct, ProductExpired

from factories import BuyerFactory, PurchaseFactory
from filters import PurchaseFilterStrategies, PaymentFilterStrategies

from segue.mailer import MailerService

from pagseguro import PagSeguroPaymentService
from boleto    import BoletoPaymentService
from models    import Purchase, Payment

import schema

class PurchaseService(object):
    def __init__(self, db_impl=None, payments=None, filters=None):
        self.db = db_impl or db
        self.payments = payments or PaymentService()
        self.filters = filters or PurchaseFilterStrategies()

    def query(self, by=None, **kw):
        filter_list = self.filters.given(**kw)
        return Purchase.query.filter(*filter_list).all()

    def create(self, buyer_data, product, account, **extra):
        buyer    = BuyerFactory.from_json(buyer_data, schema.buyer)
        purchase = PurchaseFactory.create(buyer, product, account, **extra)
        self.db.session.add(buyer)
        self.db.session.add(purchase)
        self.db.session.commit()
        return purchase

    def get_one(self, purchase_id, by=None):
        purchase = Purchase.query.get(purchase_id)
        if not purchase: return None
        if not self.check_ownership(purchase, by): raise NotAuthorized()
        return purchase

    def check_ownership(self, purchase, alleged):
        return purchase and alleged and purchase.customer_id == alleged.id

    def create_payment(self, purchase_id, payment_method, payment_data, by=None):
        purchase = self.get_one(purchase_id, by=by)
        if purchase.can_start_payment:
            return self.payments.create(purchase, payment_method, payment_data)
        raise ProductExpired()

    def clone_purchase(self, purchase_id, by=None):
        purchase = self.get_one(purchase_id, by=by)
        if not purchase: return None

        if purchase.satisfied:
            raise PurchaseAlreadySatisfied()

        replacement_product = purchase.product.similar_products().first()
        if not replacement_product:
            raise NoSuchProduct()

        cloned_purchase = purchase.clone()
        cloned_purchase.product = replacement_product
        db.session.add(cloned_purchase)
        db.session.commit()
        return cloned_purchase

class PaymentService(object):
    DEFAULT_PROCESSORS = dict(
        pagseguro = PagSeguroPaymentService,
        boleto    = BoletoPaymentService
    )

    def __init__(self, mailer=None, caravans=None, filters=None, **processors_overrides):
        from segue.caravan.services import CaravanService # THIS IS UGLY
        self.processors_overrides = processors_overrides
        self.mailer               = mailer or MailerService()
        self.caravans             = caravans or CaravanService()
        self.filters              = filters or PaymentFilterStrategies()

    def query(self, by=None, **kw):
        filter_list = self.filters.given(**kw)
        return Payment.query.filter(*filter_list).all()

    def create(self, purchase, method, data):
        if purchase.satisfied: raise PurchaseAlreadySatisfied()
        processor = self.processor_for(method)
        payment = processor.create(purchase, data)
        instructions = processor.process(payment)
        db.session.add(payment)
        db.session.commit()
        return instructions

    def get_one(self, purchase_id, payment_id):
        result = Payment.query.filter(Purchase.id == purchase_id, Payment.id == payment_id)
        return result.first()

    def conclude(self, purchase_id, payment_id, payload):
        try:
            payment = self.get_one(purchase_id, payment_id)
            if not payment: raise NoSuchPayment(purchase_id, payment_id)
            processor = self.processor_for(payment.type)
            purchase = payment.purchase
            logger.debug('selected processor for conclusion: %s', payment.type)

            transition = processor.conclude(payment, payload)
            payment.recalculate_status()
            purchase.recalculate_status()
            logger.debug('recalculated status: payment.status=%s, purchase.status=%s', payment.status, purchase.status)

            db.session.add(payment)
            db.session.add(transition)
            db.session.add(purchase)
            db.session.commit()
            return purchase
        except KeyError, e:
            logger.error('Exception was thrown while processing payment conclusion! %s', e)
            raise e

    def notify(self, purchase_id, payment_id, payload, source='notification'):
        try:
            payment = self.get_one(purchase_id, payment_id)
            if not payment: raise NoSuchPayment(purchase_id, payment_id)
            processor = self.processor_for(payment.type)
            purchase = payment.purchase
            logger.debug('selected processor for notification: %s', payment.type)

            transition = processor.notify(purchase, payment, payload, source)
            payment.recalculate_status()
            purchase.recalculate_status()
            logger.debug('recalculated status: payment.status=%s, purchase.status=%s', payment.status, purchase.status)

            db.session.add(payment)
            db.session.add(transition)
            db.session.add(purchase)
            db.session.commit()

            if purchase.satisfied:
                logger.debug('transition is good payment! notifying customer via e-mail!')
                self.mailer.notify_payment(purchase, payment)

                # TODO: improve this code, caravan concerns should never live here!
                if purchase.kind == 'caravan-rider':
                    logger.debug('attempting to exempt the leader of a caravan')
                    self.caravans.update_leader_exemption(purchase.caravan.id, purchase.caravan.owner)

            return purchase, transition
        except Exception, e:
            logger.error('Exception was thrown while processing payment notification! %s', e)
            raise e

    def processor_for(self, method):
        if method in self.processors_overrides:
            return self.processors_overrides[method]
        if method in self.DEFAULT_PROCESSORS:
            return self.DEFAULT_PROCESSORS[method]()
        raise NotImplementedError(method+' is not a valid payment method')

