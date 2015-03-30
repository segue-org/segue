from datetime import datetime, timedelta
import mockito

from segue.product import ProductService, Product
from segue.errors import ProductExpired

from ..support import SegueApiTestCase
from ..support.factories import ValidAccountFactory, ValidPurchaseFactory, ValidProductFactory

class ProductServiceTestCase(SegueApiTestCase):
    def setUp(self):
        super(ProductServiceTestCase, self).setUp()
        self.mock_purchases = mockito.Mock()
        self.service = ProductService(purchases=self.mock_purchases)

    def test_listing_all_products_ignores_unavailable_products(self):
        yesterday = datetime.now() - timedelta(days=1)
        product1 = self.create_from_factory(ValidProductFactory)
        product2 = self.create_from_factory(ValidProductFactory)
        product3 = self.create_from_factory(ValidProductFactory, sold_until=yesterday)

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

    def test_cannot_purchase_past_its_sold_date(self):
        yesterday = datetime.now() - timedelta(days=1)
        account = self.create_from_factory(ValidAccountFactory)
        product = self.create_from_factory(ValidProductFactory, sold_until=yesterday)
        purchase = self.build_from_factory(ValidPurchaseFactory)

        buyer_data = dict(mocked_data='that will be ignored')

        with self.assertRaises(ProductExpired):
            self.service.purchase(buyer_data, product.id, account=account)

