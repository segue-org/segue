from requests.exceptions import RequestException
from segue.errors import ExternalServiceError, InvalidPaymentNotification
from segue.core import db, logger

from .factories import PagSeguroPaymentFactory, PagSeguroSessionFactory, PagSeguroTransitionFactory

class PagSeguroPaymentService(object):
    def __init__(self, sessions=None):
        self.sessions = sessions or PagSeguroSessionFactory()

    def notify(self, purchase, payment, payload=None, source='notification'):
        logger.debug('received pagseguro notification with payload %s', payload)
        notification_code = payload.get('notificationCode', None)
        if not notification_code: raise InvalidPaymentNotification()

        try:
            xml_result = self.sessions.notification_session(notification_code).check()
            return PagSeguroTransitionFactory.create(notification_code, payment, xml_result, source)
        except RequestException, e:
            logger.errror('connection error to pagseguro! %s', e)
            raise ExternalServiceError('pagseguro')

    def create(self, purchase, data=None):
        payment = PagSeguroPaymentFactory.create(purchase)
        db.session.add(payment)
        db.session.commit()
        return payment

    def process(self, payment):
        payment_session = self.sessions.payment_session(payment)
        try:
            logger.debug('starting pagseguro checkout for %s...', payment.id)
            result = payment_session.checkout()
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


