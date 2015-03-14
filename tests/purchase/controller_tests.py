import json
import mockito

from segue.errors import NotAuthorized, PaymentVerificationFailed

from ..support import SegueApiTestCase
from ..support.factories import *

class PurchaseControllerTestCases(SegueApiTestCase):
    def setUp(self):
        super(PurchaseControllerTestCases, self).setUp()
        self.mock_service = self.mock_controller_dep('purchases', 'service')
        self.mock_owner   = self.mock_controller_dep('purchases', 'current_user', ValidAccountFactory.create())
        self.mock_jwt(self.mock_owner)

    def test_listing_purchases(self):
        p1 = self.build_from_factory(ValidPurchaseFactory)
        p2 = self.build_from_factory(ValidPurchaseFactory)
        mockito.when(self.mock_service).query(by=self.mock_owner).thenReturn([p1,p2])

        response = self.jget('/purchases')
        contents = json.loads(response.data)['items']

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(contents), 2)

    def test_getting_a_purchase_requires_auth(self):
        purchase = self.build_from_factory(ValidPurchaseFactory)
        mockito.when(self.mock_service).get_one(123, by=self.mock_owner).thenReturn(purchase)
        mockito.when(self.mock_service).get_one(456, by=self.mock_owner).thenRaise(NotAuthorized)

        response = self.jget('/purchases/123')
        self.assertEquals(response.status_code, 200)

        response = self.jget('/purchases/456')
        self.assertEquals(response.status_code, 403)

    def test_getting_a_purchase_returns_a_json(self):
        purchase = self.build_from_factory(ValidPurchaseFactory)
        mockito.when(self.mock_service).get_one(123, by=self.mock_owner).thenReturn(purchase)

        response = self.jget('/purchases/123')
        content = json.loads(response.data)['resource']
        self.assertEquals(content['$type'], 'Purchase.normal')
        self.assertEquals(content['status'], 'pending')

    def test_startinga_a_payment_for_a_purchase(self):
        payment  = self.build_from_factory(ValidPagSeguroPaymentFactory)
        purchase = self.build_from_factory(ValidPurchaseFactory)
        mockito.when(self.mock_service).create_payment(123, 'pagseguro', {}, by=self.mock_owner).thenReturn(payment)

        response = self.jpost('/purchases/123/pay/pagseguro', data="{}")
        content = json.loads(response.data)['resource']

        self.assertEquals(content['$type'], 'PagSeguroPayment.normal')
        self.assertEquals(content['status'], 'pending')


class PaymentControllerTestCases(SegueApiTestCase):
    def setUp(self):
        super(PaymentControllerTestCases, self).setUp()
        self.mock_service = self.mock_controller_dep('purchase_payments', 'service')

    def test_notify_a_payment_transitioned(self):
        payment = { 'abc': 123 }
        query_string = "notificationCode=ABC-123-789&notificationType=transaction"

        mockito.when(self.mock_service).notify(123, 456, 'ABC-123-789').thenReturn(payment)
        mockito.when(self.mock_service).notify(123, 789, 'ABC-123-789').thenReturn(None)
        mockito.when(self.mock_service).notify(123, 999, 'ABC-123-789').thenRaise(PaymentVerificationFailed)

        response = self.jpost('/purchases/123/payments/456/notify', query_string=query_string)
        self.assertEquals(response.status_code, 200)

        response = self.jpost('/purchases/123/payments/789/notify', query_string=query_string)
        self.assertEquals(response.status_code, 404)

        response = self.jpost('/purchases/123/payments/999/notify', query_string=query_string)
        self.assertEquals(response.status_code, 500)

        response = self.jpost('/purchases/123/payments/666/notify', query_string="")
        self.assertEquals(response.status_code, 400)
