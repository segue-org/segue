from segue.product import ProductService, Product

from ..support import SegueApiTestCase
from ..support.factories import *

class ProductServiceTestCase(SegueApiTestCase):
    def setUp(self):
        super(ProductServiceTestCase, self).setUp()
        self.service = ProductService()

    def test_listing_all_products(self):
        product1 = self.create_from_factory(ValidProductFactory)
        product2 = self.create_from_factory(ValidProductFactory)

        result = self.service.list()

        self.assertEquals(len(result), 2)
        self.assertEquals(result[0], product1)
        self.assertEquals(result[1], product2)
