import os.path
from segue.errors import NotAuthorized
from segue.core import config, db
from factories import BoletoFactory, BoletoPaymentFactory, BoletoTransitionFactory
from segue.purchase.boleto.models import BoletoTransition

class BoletoSequence(object):
    def nextval(self):
        return db.session.execute(db.Sequence('payment_id_seq'))

class BoletoPaymentService(object):
    def __init__(self, boletos=None, sequence=None, factory=None):
        self.boletos  = boletos  or BoletoFactory()
        self.sequence = sequence or BoletoSequence()
        self.factory  = factory  or BoletoPaymentFactory()

    def create(self, purchase, data=None):
        payment = self.factory.create(purchase, self.sequence.nextval())
        db.session.add(payment)
        db.session.commit()
        return payment

    def process(self, payment):
        boleto = self.boletos.create(payment)
        pdf_path = self.boletos.as_pdf(boleto, payment.document_hash, config.STORAGE_DIR)
        return self._build_instructions(pdf_path)

    def notify(self, payment, payload, source):
        if source != 'script': raise NotAuthorized()

        return BoletoTransitionFactory.create(payment, payload, source)

    def _build_instructions(self, pdf_path):
        filename = os.path.basename(pdf_path)
        return dict(
            redirectUserTo='{}/api/documents/{}'.format(config.BACKEND_URL, filename)
        )

