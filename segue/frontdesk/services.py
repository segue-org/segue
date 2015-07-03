from redis import Redis
from rq import Queue

from segue.core import config

from segue.purchase.services import PurchaseService

from errors import TicketIsNotValid
from models import Person

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

    def make_badge_for_person(self, printer, person, by_user=None):
        if not person.is_valid_ticket: raise TicketIsNotValid()

        return self.make_badge(
            name         = person.name,
            city         = person.city,
            purchase     = person.purchase,
            organization = person.organization,
            category     = person.category,
        )

    def make_badge(self, printer, by_user=None, **data):
        badge = Badge(**data)
        badge.printer = printer
        badge.issuer  = by_user
        badge.job_id  = self.printers[printer].print_badge(badge)
        db.session.add(badge)
        db.session.commit()

class PeopleService(object):
    def __init__(self, purchases=None):
        self.purchases = purchases or PurchaseService()

    def get_one(self, person_id, by_user=None):
        purchase = self.purchases.get_one(person_id, by=by_user, strict=True)
        return Person(purchase)
