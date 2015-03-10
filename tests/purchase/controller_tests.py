import json
import mockito

from segue.errors import NotAuthorized

from ..support import SegueApiTestCase
from ..support.factories import *

class PurchaseControllerTestCases(SegueApiTestCase):
    def setUp(self):
        super(PurchaseControllerTestCases, self).setUp()
        self.mock_service = self.mock_controller_dep('purchases', 'service')
        self.mock_owner   = self.mock_controller_dep('proposals', 'current_user', ValidAccountFactory.create())
        self.mock_jwt(self.mock_owner)

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
