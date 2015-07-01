import mockito

from segue.purchase.promocode import PromoCodeService

from ..support import SegueApiTestCase, hashie
from ..support.factories import *

class PromoCodeServiceTestCase(SegueApiTestCase):
    def setUp(self):
        super(PromoCodeServiceTestCase, self).setUp()
        self.mock_hasher = mockito.mock()
        self.service = PromoCodeService(hasher=self.mock_hasher)

    def test_calculates_paid_amount(self):
        promo = self.create(ValidPromoCodeFactory, hash_code="DEFG5678", discount=0.2)

        product = self.create(ValidProductFactory, price=100)
        purchase = self.create(ValidPurchaseFactory, product=product)
        payment = self.create(ValidPromoCodePaymentFactory, purchase=purchase, promocode=promo)

        self.assertEqual(payment.paid_amount, 20)
        self.assertEqual(purchase.outstanding_amount, 80)

    def test_query(self):
        payment = self.create(ValidPromoCodePaymentFactory)
        pc1 = self.create(ValidPromoCodeFactory, hash_code="ABCD1234", description="amigo do rei")
        pc2 = self.create(ValidPromoCodeFactory, hash_code="DEFG5678", payment=payment)

        result = self.service.query(hash_code="ABCD")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], pc1)

        result = self.service.query(used=True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], pc2)

        result = self.service.query(description="amigo")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], pc1)

    def test_lookup(self):
        payment = self.create(ValidPromoCodePaymentFactory)
        pc1 = self.create(ValidPromoCodeFactory, hash_code="ABCD1234", description="amigo do rei")
        pc2 = self.create(ValidPromoCodeFactory, hash_code="DEFG5678", payment=payment)

        result = self.service.lookup(q="ABCD")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], pc1)

        result = self.service.lookup(q="amigo")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], pc1)


    def test_check(self):
        payment = self.create(ValidPromoCodePaymentFactory)

        pc1 = self.create(ValidPromoCodeFactory)
        pc2 = self.create(ValidPromoCodeFactory, payment=payment)

        result = self.service.check(pc1.hash_code)
        self.assertEqual(result, pc1)

        result = self.service.check(pc2.hash_code)
        self.assertEqual(result, None)

        result = self.service.check("blabla")
        self.assertEqual(result, None)

    def test_creation(self):
        product = self.create(ValidProductFactory)
        creator = self.create(ValidAccountFactory)

        mockito.when(self.mock_hasher).generate().thenReturn('A').thenReturn('B').thenReturn('C')

        result = self.service.create(product, "empresa x", creator, 70, 3)

        self.assertEqual(len(result), 3)

        discounts = [ x.discount for x in result ]
        self.assertEqual(discounts, [ 0.7, 0.7, 0.7 ])

        products = [ x.product for x in result ]
        self.assertEqual(set(products), set([product]))

        creators = [ x.creator for x in result ]
        self.assertEqual(set(creators), set([creator]))

        hashes = [ x.hash_code for x in result ]
        self.assertEqual(hashes, ['A','B','C'])

        descriptions = [ x.description for x in result ]
        self.assertEqual(descriptions[0], 'empresa x - 1/3')
        self.assertEqual(descriptions[1], 'empresa x - 2/3')
        self.assertEqual(descriptions[2], 'empresa x - 3/3')

