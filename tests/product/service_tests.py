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

    def test_purchasing_a_product(self):
        account = self.create_from_factory(ValidAccountFactory)
        product = self.create_from_factory(ValidProductFactory)

        buyer_data = dict(
            buyer_type="person",
            buyer_name="Xica da Silva",
            buyer_document="123.456.789-00",
            buyer_contact="55 51 2345-5678",
            buyer_address="Rua dos Bobos, numero zero"
        )

        result = self.service.purchase(buyer_data, product.id, account=account)

        self.assertEquals(result.customer, account)
        self.assertEquals(result.product, product)
        self.assertEquals(result.buyer_type, 'person')
        self.assertEquals(result.buyer_name,     buyer_data['buyer_name'])
        self.assertEquals(result.buyer_document, buyer_data['buyer_document'])
        self.assertEquals(result.buyer_contact,  buyer_data['buyer_contact'])
        self.assertEquals(result.buyer_address,  buyer_data['buyer_address'])
