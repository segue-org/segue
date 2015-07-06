from datetime import timedelta
from segue.core import db
from ..models import Payment, Transition

class Weekdays():
    MONDAY    = 0
    TUESDAY   = 1
    WEDNESDAY = 2
    THURSDAY  = 3
    FRIDAY    = 4
    SATURDAY  = 5
    SUNDAY    = 6

class BoletoPayment(Payment):
    __mapper_args__ = { 'polymorphic_identity': 'boleto' }

    our_number    = db.Column(db.BigInteger, name='bo_our_number')
    due_date      = db.Column(db.Date,       name='bo_due_date')
    document_hash = db.Column(db.String(32), name='bo_document_hash')

    @property
    def extra_fields(self):
        return dict(our_number=self.our_number, due_date=self.due_date, document_hash=self.document_hash)

    @property
    def legal_due_date(self):
        tolerance_days = 0
        if self.due_date.weekday() == Weekdays.SATURDAY: tolerance_days = 2
        if self.due_date.weekday() == Weekdays.SUNDAY:   tolerance_days = 1
        return self.due_date + timedelta(days=tolerance_days)

class BoletoTransition(Transition):
    __mapper_args__ = { 'polymorphic_identity': 'boleto' }

    batch_file   = db.Column(db.Text,    name='bo_batch_file')
    batch_line   = db.Column(db.Text,    name='bo_batch_line')
    payment_date = db.Column(db.Date,    name='bo_payment_date')
    paid_amount  = db.Column(db.Numeric, name='bo_paid_amount')
    errors       = db.Column(db.Text,    name='bo_errors')
