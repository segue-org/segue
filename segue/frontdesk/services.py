from redis import Redis
from rq import Queue

from segue.core import config

class PrinterService(object):
    def __init__(self, name='default', queue_host=None, queue_password=None):
        host     = queue_host     or config.QUEUE_HOST
        password = queue_password or config.QUEUE_PASSWORD
        redis_conn = Redis(host=host, password=password)
        self.queue = Queue(name, connection=redis_conn)

    def print_badge(self, value):
        return self.queue.enqueue('worker.print_badge', value)

class BadgeService(object):
    def __init__(self, override_config=None):
        self.config = override_config or config
        self.printers = { name: PrinterService(name) for name in config.PRINTERS }

    def make_badge_for_person(self, printer, person, by_user=None):
        return self.make_badge(
            name         = person.name,
            city         = person.city,
            purchase     = person.purchase,
            organization = person.organization,
            category     = person.category
        )

    def make_badge(self, printer, by_user=None, **data):
        badge = Badge(**data)
        badge.issuer = by_user
        db.session.add(badge)
        db.session.commit()
        return self.printers[printer].print_badge(**data)
