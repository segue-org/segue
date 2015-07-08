from datetime import timedelta
from segue.core import db
from ..models import Payment, Transition

class CashPayment(Payment):
    __mapper_args__ = { 'polymorphic_identity': 'cash' }

    @property
    def extra_fields(self):
        payment_transition = filter(lambda x: x.is_payment, self.transitions)
        if not payment_transition: return dict()

        return dict(
                cashier    = payment_transition[0].cashier.name,
                ip_address = payment_transition[0].ip_address,
                mode       = payment_transition[0].mode
        )

class CashTransition(Transition):
    __mapper_args__ = { 'polymorphic_identity': 'cash' }

    cashier_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    ip_address = db.Column(db.String, name='ca_ip_address')
    mode       = db.Column(db.Text, name='ca_mode')

    cashier = db.relationship('Account')

