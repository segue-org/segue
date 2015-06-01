from datetime import datetime

from sqlalchemy.sql import functions as func
from ..json import JsonSerializable, SQLAlchemyJsonSerializer
from ..core import db

from serializers import *

class Buyer(JsonSerializable, db.Model):
    _serializers = [ BuyerJsonSerializer ]
    id              = db.Column(db.Integer, primary_key=True)
    kind            = db.Column(db.Enum('person','company','government', name="buyer_kinds"))
    name            = db.Column(db.Text)
    document        = db.Column(db.Text)
    contact         = db.Column(db.Text)
    address_street  = db.Column(db.Text)
    address_number  = db.Column(db.Text)
    address_extra   = db.Column(db.Text)
    address_zipcode = db.Column(db.Text)
    address_city    = db.Column(db.Text)
    address_country = db.Column(db.Text)
    purchases       = db.relationship('Purchase', backref='buyer')

    @property
    def address_fields(self):
        result = {}
        for field in self.__mapper__.iterate_properties:
            if field.key.startswith('address_'):
                name = field.key.split("_")[-1]
                result[name] = getattr(self, field.key) or ''
        return result

    @property
    def complete_address(self):
        return u"{street} {number} {extra} - {city} {country}".format(**self.address_fields)

class Purchase(JsonSerializable, db.Model):
    _serializers = [ PurchaseJsonSerializer, ShortPurchaseJsonSerializer ]

    id             = db.Column(db.Integer, primary_key=True)
    product_id     = db.Column(db.Integer, db.ForeignKey('product.id'))
    customer_id    = db.Column(db.Integer, db.ForeignKey('account.id'))
    buyer_id       = db.Column(db.Integer, db.ForeignKey('buyer.id'))
    status         = db.Column(db.Text, default='pending')
    created        = db.Column(db.DateTime, default=func.now())
    last_updated   = db.Column(db.DateTime, onupdate=datetime.now)
    kind           = db.Column(db.Text, server_default='single')

    payments       = db.relationship('Payment', backref='purchase', lazy='dynamic')

    __tablename__ = 'purchase'
    __mapper_args__ = { 'polymorphic_on': kind, 'polymorphic_identity': 'single' }

    @property
    def valid_payments(self):
        return self.payments.filter(Payment.status.in_(Payment.VALID_PAYMENT_STATUSES))

    @property
    def paid_amount(self):
        return self.valid_payments.with_entities(func.sum(Payment.amount)).first()[0] or 0

    @property
    def outstanding_amount(self):
        return self.product.price - self.paid_amount

    @property
    def satisfied(self):
        return self.status == 'paid'

    @property
    def description(self):
        return self.product.description

    @property
    def can_start_payment(self):
        return self.product.sold_until >= datetime.now()

    def recalculate_status(self):
        self.status = 'paid' if self.outstanding_amount == 0 else 'pending'

    def clone(self):
        arguments = dict()
        for name, column in self.__mapper__.columns.items():
            if name == 'created': continue
            if not (column.primary_key or column.unique):
                arguments[name] = getattr(self, name)
        return self.__class__(**arguments)


class PaymentJsonSerializer(SQLAlchemyJsonSerializer):
    _serializer_name = 'normal'

class Payment(JsonSerializable, db.Model):
    VALID_PAYMENT_STATUSES = ['paid','confirmed']

    _serializers = [ PaymentJsonSerializer ]
    id          = db.Column(db.Integer, primary_key=True)
    type        = db.Column(db.String(20))
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id'))
    status      = db.Column(db.Text, default='pending')
    amount      = db.Column(db.Numeric)

    transitions = db.relationship('Transition', backref='payment', lazy='dynamic')

    __tablename__ = 'payment'
    __mapper_args__ = { 'polymorphic_on': type, 'polymorphic_identity': 'payment' }

    @property
    def most_recent_transition(self):
        return self.transitions.order_by(Transition.created.desc()).first()

    def recalculate_status(self):
        self.status = self.most_recent_transition.new_status

class Transition(JsonSerializable, db.Model):
    _serializers   = [ TransitionJsonSerializer ]
    id             = db.Column(db.Integer, primary_key=True)
    type           = db.Column(db.String(20))
    payment_id     = db.Column(db.Integer, db.ForeignKey('payment.id'))
    old_status     = db.Column(db.Text)
    new_status     = db.Column(db.Text)
    source         = db.Column(db.Text)
    created        = db.Column(db.DateTime, default=func.now())

    __tablename__ = 'transition'
    __mapper_args__ = { 'polymorphic_on': type, 'polymorphic_identity': 'transition' }

    @property
    def is_payment(self):
        return self.old_status != 'paid' and self.old_status == 'paid'

