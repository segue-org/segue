from segue.core import db
from ..models import Payment, Transition

class BoletoPayment(Payment):
    __mapper_args__ = { 'polymorphic_identity': 'boleto' }

    our_number    = db.Column(db.Integer,    name='bo_our_number')
    due_date      = db.Column(db.Date,       name='bo_due_date')
    document_hash = db.Column(db.String(32), name='bo_document_hash')

class BoletoTransition(Transition):
    __mapper_args__ = { 'polymorphic_identity': 'boleto' }

    batch_file   = db.Column(db.Text,    name='bo_batch_file')
    batch_line   = db.Column(db.Text,    name='bo_batch_line')
    payment_date = db.Column(db.Date,    name='bo_payment_date')
    paid_amount  = db.Column(db.Numeric, name='bo_paid_amount')
    errors       = db.Column(db.Text,    name='bo_errors')
