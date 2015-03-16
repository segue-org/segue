from requests.exceptions import RequestException
from segue.errors import ExternalServiceError
from segue.core import db, logger

from .factories import PagSeguroPaymentFactory, PagSeguroSessionFactory

class PagSeguroPaymentService(object):
    def __init__(self, session_factory=None):
        self.session_factory = session_factory or PagSeguroSessionFactory()

    def create(self, purchase, data=None):
        payment = PagSeguroPaymentFactory.create(purchase)
        db.session.add(payment)
        db.session.commit()
        return payment

    def process(self, payment):
        session = self.session_factory.create_session(payment)
        try:
            logger.debug('starting pagseguro checkout for %s...', payment.id)
            result = session.checkout()
            logger.debug('completed checkout for %s. result is: %s', payment.id, result.payment_url)
            return self._build_instructions(result)
        except RequestException, e:
            logger.error('connection error to pagseguro! %s', e)
            raise ExternalServiceError('pagseguro')

    def _build_instructions(self, result):
        if result.payment_url and isinstance(result.payment_url, str) and result.payment_url.startswith('https'):
            return dict(redirectUserTo=result.payment_url)
        logger.error('pagseguro error: invalid payment_url')
        raise ExternalServiceError('pagseguro')


