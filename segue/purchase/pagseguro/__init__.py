import pagseguro

from segue.core import db

from .factories import PagSeguroPaymentFactory, PagSeguroSessionFactory

class PagSeguroPaymentService(object):
    def __init__(self, session_factory=None):
        self.session_factory = session_factory or PagSeguroSessionFactory()

    def create(self, purchase, data={}):
        payment = PagSeguroPaymentFactory.create(purchase)
        db.session.add(payment)
        db.session.commit()
        return payment

    def process(self, payment):
        session = self.session_factory.create_session(payment)
        # TODO tratar casos de erro
        result = session.checkout()
        instructions = dict(redirectUserTo=result.payment_url)
        return instructions

