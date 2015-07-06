import jsonschema
from redis import Redis
from rq import Queue

from segue.core import db, config, logger
from segue.filters import FilterStrategies
from segue.errors import SegueValidationError
from segue.hasher import Hasher
from segue.mailer import MailerService

from segue.models import Purchase, PromoCode, PromoCodePayment, Account
from segue.account.services import AccountService
from segue.purchase.services import PurchaseService
from segue.product.services import ProductService

from errors import TicketIsNotValid
from models import Person, Badge, Visitor
import schema

def _validate(schema_name, data):
    validator = jsonschema.Draft4Validator(schema.whitelist.get(schema_name), format_checker=jsonschema.FormatChecker())
    errors = list(validator.iter_errors(data))
    if errors:
        logger.error('validation error for person patch: %s', errors)
        raise SegueValidationError(errors)

class PrinterService(object):
    def __init__(self, name='default', queue_host=None, queue_password=None):
        host     = queue_host     or config.QUEUE_HOST
        password = queue_password or config.QUEUE_PASSWORD
        redis_conn = Redis(host=host, password=password)
        self.queue = Queue(name, connection=redis_conn)

    def print_badge(self, badge):
        return self.queue.enqueue('worker.print_badge', badge.print_data())

class BadgeService(object):
    def __init__(self, override_config=None):
        self.config = override_config or config
        self.printers = { name: PrinterService(name) for name in config.PRINTERS }

    def latest_attempt_for_person(self, person_id):
        return Badge.query.filter(Badge.person_id == person_id).order_by(Badge.created.desc()).first()

    def was_ever_printed(self, person_id):
        return self.latest_attempt_for_person(person_id) != None

    def has_failed_recently(self, person_id):
        latest_attempt = self.latest_attempt_for_person(person_id)
        if not latest_attempt: return False
        return latest_attempt.result == 'failed'

    def mark_failed_for_person(self, person_id):
        lattest_attempt = self.latest_attempt_for_person(person_id)
        if not latest_attempt: return False
        latest_attempt.result = 'failed'
        db.session.add(latest_attempt)
        db.session.commit()
        return True

    def report_failure(self, job_id):
        badge = Badge.query.filter(Badge.job_id == job_id).first()
        if not badge: return False
        if badge.result == 'failed': return False
        badge.result = 'failed'
        db.session.add(badge)
        db.session.commit()
        return True

    def report_success(self, job_id):
        badge = Badge.query.filter(Badge.job_id == job_id).first()
        if not badge: return False
        if badge.result == 'success': return False
        badge.result = 'success'
        db.session.add(badge)
        db.session.commit()
        return True

    def make_badge(self, printer, visitor_or_person, copies=1, by_user=None):
        if not visitor_or_person.can_print_badge: raise CannotPrintBadge()
        badge = Badge.create(visitor_or_person)
        badge.printer = printer
        badge.issuer  = by_user
        badge.copies  = copies
        badge.job_id  = self.printers[printer].print_badge(badge).id
        db.session.add(badge)
        db.session.commit()

class VisitorService(object):
    def __init__(self, badges=None):
        self.badges = badges or BadgeService()

    def create(self, printer, by_user=None, **data):
        _validate('visitor', data)
        visitor = Visitor(**data)
        db.session.add(visitor)
        db.session.commit()
        self.badges.make_badge(printer, visitor, by_user=by_user)
        return visitor


class PeopleService(object):
    def __init__(self, purchases=None, filters=None, products=None, accounts=None, hasher=None, mailer=None):
        self.products  = products  or ProductService()
        self.purchases = purchases or PurchaseService()
        self.accounts  = accounts  or AccountService()
        self.filters   = filters   or FrontDeskFilterStrategies()
        self.hasher    = hasher    or Hasher()
        self.mailer    = mailer    or MailerService()

    def get_by_hash(self, hash_code):
        purchase = self.purchases.get_by_hash(hash_code, strict=True)
        return Person(purchase)

    def send_reception_mail(self, person_id):
        purchase = self.purchases.get_one(person_id, strict=True, check_ownership=False)

        if not purchase.hash_code:
            purchase.hash_code = self.hasher.generate()
            db.session.add(purchase)
            db.session.commit()

        person = Person(purchase)
        self.mailer.reception_mail(person)
        return person

    def by_range(self, start, end):
        purchases = self.purchases.by_range(start, end).all()
        return map(Person, purchases)

    def get_one(self, person_id, by_user=None, check_ownership=True, strict=True):
        purchase = self.purchases.get_one(person_id, by=by_user, strict=True, check_ownership=check_ownership)
        if purchase: return Person(purchase)
        if strict: raise NoSuchPurchase()
        return None

    def lookup(self, needle, by_user=None, limit=20):
        base    = self.filters.all_joins(Purchase.query)
        filters = self.filters.needle(needle)
        query   = base.filter(*filters).order_by(Purchase.status, Purchase.id).limit(limit)
        return map(Person, query.all())

    def set_product(self, person_id, new_product_id):
        purchase = self.purchases.get_one(person_id, check_ownership=False, strict=True)
        product  = self.products.get_product(new_product_id)

        purchase.product = product
        purchase.kind    = product.special_purchase_class() or purchase.kind

        db.session.add(purchase)
        db.session.commit()
        db.session.expunge_all()

        return self.get_one(person_id, strict=True, check_ownership=False)


    def create(self, email, by_user=None):
        _validate('create', dict(email=email))

        default_product = self.products.cheapest_for('normal')
        account = self.accounts.create_for_email(email, commit=False)
        purchase = Purchase(customer=account, product=default_product)

        db.session.add(purchase)
        db.session.commit()

        return Person(purchase)

    def patch(self, person_id, by_user=None, **data):
        purchase = self.purchases.get_one(person_id, by=by_user, strict=True)

        _validate('patch', data)

        for key, value in data.items():
            method = getattr(self, "_patch_"+key, None)
            if method: method(purchase, value)

        db.session.add(purchase)
        db.session.commit()

        return Person(purchase)

    def _patch_name(self, purchase, value):
        purchase.customer.name = value
        db.session.add(purchase.customer)

    def _patch_city(self, purchase, value):
        purchase.customer.city = value
        db.session.add(purchase.customer)

    def _patch_document(self, purchase, value):
        purchase.customer.document = value
        db.session.add(purchase.customer)

    def _patch_country(self, purchase, value):
        purchase.customer.country = value
        db.session.add(purchase.customer)

class FrontDeskFilterStrategies(FilterStrategies):
    def by_customer_id(self, value, as_user=None):
        if isinstance(value, basestring) and not value.isdigit(): return
        return Purchase.id == value

    def by_customer_name(self, value, as_user=None):
        if isinstance(value, basestring) and value.isdigit(): return
        value = value.replace(" ","%")
        return Account.name.ilike('%'+value+'%')

    def by_customer_email(self, value, as_user=None):
        if isinstance(value, basestring) and "@" in value:
            return Account.email.ilike('%'+value+'%')

    def join_for_customer_name(self, queryset, needle=None):
        if isinstance(needle, basestring) and needle.isdigit():
            return queryset
        else:
            return queryset.join('customer')

    def join_for_customer_email(self, queryset, needle=None):
        if isinstance(needle, basestring) and "@" in needle:
            return queryset.join('customer')
        else:
            return queryset
