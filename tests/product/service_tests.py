from datetime import datetime, timedelta
import mockito

from segue.product.services import ProductService
from segue.product.models import Product
from segue.caravan.models import CaravanProduct
from segue.caravan.errors import InvalidCaravan
from segue.product.errors import ProductExpired, WrongBuyerForProduct

from ..support import SegueApiTestCase
from ..support.factories import *

class ProductServiceTestCase(SegueApiTestCase):
    def setUp(self):
        super(ProductServiceTestCase, self).setUp()
        self.mock_purchases = mockito.Mock()
        self.mock_caravans  = mockito.Mock()
        self.service = ProductService(purchases=self.mock_purchases, caravans=self.mock_caravans)

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

        product1 = self.create_from_factory(ValidCaravanProductFactory, sold_until=next_week)
        product2 = self.create_from_factory(ValidCaravanProductFactory, sold_until=tomorrow)
        product3 = self.create_from_factory(ValidProductFactory,        sold_until=tomorrow)
        product4 = self.create_from_factory(ValidStudentProductFactory, sold_until=yesterday)

        mockito.when(self.mock_caravans).invite_by_hash('123ABC').thenReturn('fake-invite')
        mockito.when(self.mock_caravans).invite_by_hash('456DEF').thenReturn(None)

        result = self.service.caravan_products("123ABC")

        self.assertEquals(len(result), 2)
        self.assertEquals(result[1], product1)
        self.assertEquals(result[0], product2)
        self.assertIsInstance(result[0], CaravanProduct)
        self.assertIsInstance(result[1], CaravanProduct)

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

    def test_can_only_purchase_caravan_with_valid_hash(self):
        tomorrow = datetime.now() + timedelta(days=1)
        account = self.create_from_factory(ValidAccountFactory)
        product = self.create_from_factory(ValidCaravanProductFactory, sold_until=tomorrow)
        invite = self.create_from_factory(ValidCaravanInviteFactory, hash='123888')
        fake_purchase = self.build_from_factory(ValidPurchaseFactory)

        buyer_data = dict(caravan_invite_hash='123888')
        mockito.when(self.mock_purchases).create(buyer_data, product, account, caravan=invite.caravan).thenReturn(fake_purchase)

        result = self.service.purchase(buyer_data, product.id, account=account)

        self.assertEquals(result, fake_purchase)

        with self.assertRaises(WrongBuyerForProduct):
            self.service.purchase(dict(caravan_invite_hash='XXXXXX'), product.id, account=account)


