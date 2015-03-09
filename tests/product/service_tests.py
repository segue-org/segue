import mockito

from segue.product import ProductService, Product

from ..support import SegueApiTestCase
from ..support.factories import *

class ProductServiceTestCase(SegueApiTestCase):
    def setUp(self):
        super(ProductServiceTestCase, self).setUp()
        self.mock_purchases = mockito.Mock()
        self.service = ProductService(purchases=self.mock_purchases)

    def test_listing_all_products(self):
        product1 = self.create_from_factory(ValidProductFactory)
        product2 = self.create_from_factory(ValidProductFactory)

        result = self.service.list()

        self.assertEquals(len(result), 2)
        self.assertEquals(result[0], product1)
        self.assertEquals(result[1], product2)

    def test_purchasing_a_product(self):
        account = self.create_from_factory(ValidAccountFactory)
        product = self.create_from_factory(ValidProductFactory)
        purchase = self.build_from_factory(ValidPurchaseFactory)

        buyer_data = dict(mocked_data='that will be ignored')

        mockito.when(self.mock_purchases).create(buyer_data, product, account).thenReturn(purchase)

        result = self.service.purchase(buyer_data, product.id, account=account)

        self.assertEquals(result, purchase)
