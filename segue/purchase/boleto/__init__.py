from segue.core import db
from factories import BoletoFactory, BoletoPaymentFactory

class BoletoSequence(object):
    def nextval(self):
        return db.session.execute(db.Sequence('payment_id_seq'))

class BoletoPaymentService(object):
    def __init__(self, boletos=None, sequence=None):
        self.boletos  = boletos  or BoletoFactory()
        self.sequence = sequence or BoletoSequence()

    def create(self, purchase, data=None):
        payment = BoletoPaymentFactory.create(purchase, self.sequence.nextval())
        db.session.add(payment)
        db.session.commit()
        return payment

    def process(self, payment):
        boleto = self.boletos.create(payment)
        pdf_path = self.boletos.as_pdf(boleto, payment.document_hash)
        return self._build_instructions(pdf_path)

    def _build_instructions(self, pdf_path):
        return dict(redirectUserTo='')

