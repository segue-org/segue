from redis import Redis
from rq import Queue

from segue.core import db, config
from segue.filters import FilterStrategies

from segue.purchase.services import PurchaseService

from errors import TicketIsNotValid
from models import Person, Badge
from segue.models import Purchase, PromoCode, PromoCodePayment, Account

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

    def make_badge_for_person(self, printer, person, copies=1, by_user=None):
        if not person.is_valid_ticket: raise TicketIsNotValid()

        badge = Badge.create_for_person(person)
        badge.printer = printer
        badge.issuer  = by_user
        badge.copies  = copies
        badge.job_id  = self.printers[printer].print_badge(badge).id
        db.session.add(badge)
        db.session.commit()

    def make_badge(self, printer, by_user=None, copies=1, **data):
        badge = Badge(**data)
        badge.printer = printer
        badge.issuer  = by_user
        badge.copies  = copies
        badge.job_id  = self.printers[printer].print_badge(badge).id
        db.session.add(badge)
        db.session.commit()

class PeopleService(object):
    def __init__(self, purchases=None, filters=None):
        self.purchases = purchases or PurchaseService()
        self.filters   = filters   or FrontDeskFilterStrategies()

    def get_one(self, person_id, by_user=None):
        purchase = self.purchases.get_one(person_id, by=by_user, strict=True)
        return Person(purchase)

    def lookup(self, needle, by_user=None, limit=20):
        base    = self.filters.all_joins(Purchase.query)
        filters = self.filters.needle(needle)
        query   = base.filter(*filters).order_by(Purchase.status, Purchase.id).limit(limit)
        return map(Person, query.all())

class FrontDeskFilterStrategies(FilterStrategies):
    def by_customer_id(self, value, as_user=None):
        if isinstance(value, basestring) and not value.isdigit(): return
        return Purchase.id == value

    def by_customer_name(self, value, as_user=None):
        if isinstance(value, basestring) and value.isdigit(): return
        return Account.name.ilike('%'+value+'%')

    def join_for_customer_name(self, queryset, needle=None):
        if isinstance(needle, basestring) and needle.isdigit():
            return queryset
        else:
            return queryset.join(Account)
