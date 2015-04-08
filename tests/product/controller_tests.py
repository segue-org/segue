import json
import mockito

from segue.product import ProductController

from ..support import SegueApiTestCase
from ..support.factories import *

class ProductControllerTestCases(SegueApiTestCase):
    def setUp(self):
        super(ProductControllerTestCases, self).setUp()
        self.mock_service = self.mock_controller_dep('products', 'service')
        self.mock_owner   = self.mock_controller_dep('proposals', 'current_user', ValidAccountFactory.create())
        self.mock_jwt(self.mock_owner)

    def test_list_available_products(self):
        product1 = ValidProductFactory.build()
        product2 = ValidProductFactory.build()
        mockito.when(self.mock_service).list().thenReturn([ product1, product2 ])

        response = self.jget('/products')
        items = json.loads(response.data)['items']

        self.assertEquals(len(items), 2)

    def test_list_caravan_products(self):
        product1 = ValidProductFactory.build()
        product2 = ValidProductFactory.build()
        mockito.when(self.mock_service).caravan_products("123ABC").thenReturn([product1, product2])

        response = self.jget('/products/caravan/123ABC')
        items = json.loads(response.data)['items']

        self.assertEquals(len(items), 2)


    def test_purchase_product(self):
        data = { "arbitrary": "json that will be mocked out anyway" }
        raw_json = json.dumps(data)
        purchase = ValidPurchaseByPersonFactory.build()
        mockito.when(self.mock_service).purchase(data, 789, account=self.mock_owner).thenReturn(purchase)

        response = self.jpost('/products/789/purchase', data=raw_json)
        content = json.loads(response.data)['resource']

        self.assertEquals(content['$type'], 'Purchase.normal')
