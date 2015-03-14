import mockito

from segue.purchase.pagseguro import PagSeguroPaymentService
from segue.purchase.models import PagSeguroPayment

from ..support import SegueApiTestCase, hashie
from ..support.factories import *

class PagSeguroPaymentServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(PagSeguroPaymentServiceTestCases, self).setUp()
        self.pagseguro = mockito.Mock()
        self.service = PagSeguroPaymentService(session_factory=self.pagseguro)

    def test_creates_a_payment_on_db(self):
        account = self.create_from_factory(ValidAccountFactory, id=333)
        purchase = self.create_from_factory(ValidPurchaseFactory, id=666, customer=account)

        result = self.service.create(purchase, {})

        self.assertEquals(result.type, 'pagseguro')
        self.assertEquals(result.__class__, PagSeguroPayment)
        self.assertEquals(result.status, 'pending')
        self.assertEquals(result.reference, 'A00333-PU00666')
        self.assertEquals(result.amount, purchase.product.price)

    def test_processes_a_pagseguro_checkout(self):
        payment = self.create_from_factory(ValidPagSeguroPaymentFactory)
        session = mockito.Mock()

        mockito.when(self.pagseguro).create_session(payment).thenReturn(session)
        mockito.when(session).checkout().thenReturn(hashie(payment_url='http://songa'))

        result = self.service.process(payment)

        self.assertEquals(result['redirectUserTo'], 'http://songa')
