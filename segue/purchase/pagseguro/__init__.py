from requests.exceptions import RequestException
from segue.errors import ExternalServiceError, InvalidPaymentNotification, NoSuchPayment
from segue.core import db, logger

from .factories import PagSeguroPaymentFactory, PagSeguroSessionFactory, PagSeguroTransitionFactory

class PagSeguroPaymentService(object):
    def __init__(self, sessions=None):
        self.sessions = sessions or PagSeguroSessionFactory()

    def notify(self, purchase, payment, payload=None, source='notification'):
        logger.debug('received pagseguro direct notification with payload %s', payload)
        notification_code = payload.get('notificationCode', None)
        if not notification_code: raise InvalidPaymentNotification()

        try:
            xml_result = self.sessions.notification_session(notification_code).check()
            return PagSeguroTransitionFactory.create(notification_code, payment, xml_result, source)
        except RequestException, e:
            logger.error('connection error to pagseguro! %s', e)
            raise ExternalServiceError('pagseguro')

    def create(self, purchase, data=None):
        payment = PagSeguroPaymentFactory.create(purchase)
        db.session.add(payment)
        db.session.commit()
        return payment

    def conclude(self, payment, payload=None):
        logger.debug('received pagseguro conclude notification with payload %s', payload)
        transaction_id = payload.get('transaction_id', None)
        if not transaction_id: raise InvalidPaymentNotification()

        try:
            xml_result = self.sessions.query_session(transaction_id).get()
            return PagSeguroTransitionFactory.create(transaction_id, payment, xml_result, 'conclude')
        except RequestException, e:
            logger.error('connection error to pagseguro! %s', e)
            raise ExternalServiceError('pagseguro')

    def process(self, payment):
        payment_session = self.sessions.payment_session(payment)
        try:
            logger.debug('starting pagseguro checkout for %s...', payment.id)
            result = payment_session.checkout()
            logger.debug('pagseguro answered with xml... %s', result.xml)
            logger.debug('completed checkout for %s. result is: %s', payment.id, result.payment_url)
            instructions = self._build_instructions(result)
            payment.code = result.code
            return instructions
        except RequestException, e:
            logger.error('connection error to pagseguro! %s', e)
            raise ExternalServiceError('pagseguro')

    def _build_instructions(self, result):
        url = result.payment_url or ''
        if url.startswith('https'):
            return dict(redirectUserTo=result.payment_url)
        logger.error('pagseguro error: invalid payment_url')
        raise ExternalServiceError('pagseguro')


