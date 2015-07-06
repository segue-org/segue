from segue.core import db
from ..models import Payment, Transition

class PagSeguroPayment(Payment):
    __mapper_args__ = { 'polymorphic_identity': 'pagseguro' }

    reference = db.Column(db.String(50), name='ps_reference')
    code      = db.Column(db.String(32), name='ps_code')

    @property
    def extra_fields(self):
        return dict(reference=self.reference, code=self.code)

class PagSeguroTransition(Transition):
    __mapper_args__ = { 'polymorphic_identity': 'pagseguro' }
    notification_code = db.Column(db.String(39), name='ps_notification_code')
    payload           = db.Column(db.Text,       name='ps_payload')
