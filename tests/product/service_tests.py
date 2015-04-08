from datetime import datetime, timedelta
import mockito

from segue.product import ProductService, Product
from segue.errors import ProductExpired, InvalidCaravan

from ..support import SegueApiTestCase
from ..support.factories import ValidAccountFactory, ValidPurchaseFactory, ValidProductFactory

class ProductServiceTestCase(SegueApiTestCase):
    def setUp(self):
        super(ProductServiceTestCase, self).setUp()
        self.mock_purchases       = mockito.Mock()
        self.mock_caravan_invites = mockito.Mock()
        self.service = ProductService(purchases=self.mock_purchases, caravan_invites=self.mock_caravan_invites)

    def test_listing_all_products_ignores_unavailable_products(self):
        yesterday = datetime.now() - timedelta(days=1)
        tomorrow  = datetime.now() + timedelta(days=1)
        next_week = datetime.now() + timedelta(weeks=1)

        product1 = self.create_from_factory(ValidProductFactory, sold_until=next_week)
        product2 = self.create_from_factory(ValidProductFactory, sold_until=tomorrow)
        product3 = self.create_from_factory(ValidProductFactory, sold_until=yesterday)

        result = self.service.list()

        self.assertEquals(len(result), 2)
        self.assertEquals(result[1], product1)
        self.assertEquals(result[0], product2)

    def test_list_caravan_products(self):
        yesterday = datetime.now() - timedelta(days=1)
        tomorrow  = datetime.now() + timedelta(days=1)
        next_week = datetime.now() + timedelta(weeks=1)

        product1 = self.create_from_factory(ValidProductFactory, category='caravan', sold_until=next_week)
        product2 = self.create_from_factory(ValidProductFactory, category='caravan', sold_until=tomorrow)
        product3 = self.create_from_factory(ValidProductFactory, category='person',  sold_until=tomorrow)
        product4 = self.create_from_factory(ValidProductFactory, category='student', sold_until=yesterday)

        mockito.when(self.mock_caravan_invites).get_by_hash('123ABC').thenReturn('fake-invite')
        mockito.when(self.mock_caravan_invites).get_by_hash('456DEF').thenReturn(None)

        result = self.service.caravan_products("123ABC")

        self.assertEquals(len(result), 2)
        self.assertEquals(result[1], product1)
        self.assertEquals(result[0], product2)

        with self.assertRaises(InvalidCaravan):
            self.service.caravan_products('456DEF')



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

