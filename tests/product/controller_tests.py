import json
import mockito

from segue.product import ProductController

from ..support import SegueApiTestCase
from ..support.factories import *

class ProductControllerTestCases(SegueApiTestCase):
    def setUp(self):
        super(ProductControllerTestCases, self).setUp()
        self.mock_service = self.mock_controller_dep('products', 'service')

    def test_list_available_products(self):
        product1 = ValidProductFactory.build()
        product2 = ValidProductFactory.build()
        mockito.when(self.mock_service).list().thenReturn([ product1, product2 ])

        response = self.jget('/products')
        items = json.loads(response.data)['items']

        self.assertEquals(len(items), 2)
