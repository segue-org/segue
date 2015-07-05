from datetime import datetime
from segue.core import db
from sqlalchemy.sql import functions as func

class Badge(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    person_id    = db.Column(db.Integer, db.ForeignKey('purchase.id'))
    issuer_id    = db.Column(db.Integer, db.ForeignKey('account.id'))
    copies       = db.Column(db.Integer, default=1)
    printer      = db.Column(db.Text)
    name         = db.Column(db.Text)
    organization = db.Column(db.Text)
    city         = db.Column(db.Text)
    category     = db.Column(db.Text)
    job_id       = db.Column(db.Text)
    result       = db.Column(db.Text)

    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.now)

    person       = db.relationship('Purchase', backref=db.backref('badges', lazy='dynamic'))

    @classmethod
    def create_for_person(cls, person):
        badge = Badge(person=person.purchase)
        badge.name         = person.name
        badge.city         = person.city
        badge.category     = person.category
        badge.organization = person.organization
        return badge

    @property
    def xid(self):
        return self.person.id if self.person else None

    def print_data(self):
        return dict(
            xid          = self.xid,
            name         = self.name,
            city         = self.city,
            organization = self.organization,
            category     = self.category,
            copies       = self.copies
        )

class Person(object):
    def __init__(self, purchase, links=False):
        self.id           = purchase.id
        self.name         = purchase.customer.name
        self.email        = purchase.customer.email
        self.document     = purchase.customer.document
        self.organization = purchase.customer.organization
        self.city         = purchase.customer.city
        self.country      = purchase.customer.country
        self.category     = purchase.product.category
        self.price        = purchase.product.price
        self.status       = purchase.status
        self.buyer        = purchase.buyer
        self.purchase     = purchase

    @property
    def related_people(self):
        all_purchases = self.purchase.customer.purchases[:]
        other_purchases = [ x for x in all_purchases if x.id != self.id ]
        return map(Person, other_purchases)

    @property
    def related_count(self):
        return len(self.purchase.customer.purchases) - 1

    @property
    def is_valid_ticket(self):
        return self.status == 'paid'

    @property
    def eligible_products(self):
        return []
