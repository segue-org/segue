from datetime import timedelta
from segue.core import db
from ..models import Payment, Transition

class CashPayment(Payment):
    __mapper_args__ = { 'polymorphic_identity': 'cash' }

class CashTransition(Transition):
    __mapper_args__ = { 'polymorphic_identity': 'cash' }

    cashier_id  = db.Column(db.Integer, db.ForeignKey('account.id'))
    ip_address  = db.Column(db.String, name='ca_ip_address')

    @property
    def extra_fields(self):
        return dict(cashier=self.cashier.name, ip_address=self.ip_address)
