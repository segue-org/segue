import datetime

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

class Purchase(JsonSerializable, db.Model):
    _serializers = [ PurchaseJsonSerializer, ShortPurchaseJsonSerializer ]
    id             = db.Column(db.Integer, primary_key=True)
    product_id     = db.Column(db.Integer, db.ForeignKey('product.id'))
    customer_id    = db.Column(db.Integer, db.ForeignKey('account.id'))
    buyer_id       = db.Column(db.Integer, db.ForeignKey('buyer.id'))
    status         = db.Column(db.Text, default='pending')
    created        = db.Column(db.DateTime, default=func.now())
    last_updated   = db.Column(db.DateTime, onupdate=datetime.datetime.now)

    payments       = db.relationship('Payment', backref='purchase', lazy='dynamic')

    @property
    def valid_payments(self):
        return self.payments.filter(Payment.status.in_(Payment.VALID_PAYMENT_STATUSES))

    @property
    def paid_amount(self):
        return self.valid_payments.with_entities(func.sum(Payment.amount)).first()[0] or 0

    @property
    def outstanding_amount(self):
        return self.product.price - self.paid_amount

    def recalculate_status(self):
        self.status = 'paid' if self.outstanding_amount == 0 else 'pending'

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

class PagSeguroPayment(Payment):
    __mapper_args__ = { 'polymorphic_identity': 'pagseguro' }

    reference = db.Column(db.String(50), name='ps_reference')
    code      = db.Column(db.String(32), name='ps_code')

class Transition(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    type           = db.Column(db.String(20))
    payment_id     = db.Column(db.Integer, db.ForeignKey('payment.id'))
    old_status     = db.Column(db.Text)
    new_status     = db.Column(db.Text)
    source         = db.Column(db.Text)
    created        = db.Column(db.DateTime, default=func.now())

    __tablename__ = 'transition'
    __mapper_args__ = { 'polymorphic_on': type, 'polymorphic_identity': 'transition' }

class PagSeguroTransition(Transition):
    __mapper_args__ = { 'polymorphic_identity': 'pagseguro' }
    notification_code = db.Column(db.String(39), name='ps_notification_code')
    payload           = db.Column(db.Text,       name='ps_payload')
