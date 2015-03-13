import mockito

from segue.purchase import PurchaseService, PaymentService
from segue.purchase.models import Payment, PagSeguroPayment
from segue.errors import NotAuthorized

from ..support import SegueApiTestCase
from ..support.factories import *


class PurchaseServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(PurchaseServiceTestCases, self).setUp()
        self.service = PurchaseService()

    def test_purchasing_a_product(self):
        account    = self.create_from_factory(ValidAccountFactory)
        product    = self.create_from_factory(ValidProductFactory)
        buyer_data = self.build_from_factory(ValidBuyerPersonFactory).to_json()

        result = self.service.create(buyer_data, product, account)

        self.assertEquals(result.customer, account)
        self.assertEquals(result.product, product)
        self.assertEquals(result.status, 'pending')
        self.assertEquals(result.buyer.name, buyer_data['name'])
        self.assertEquals(result.buyer.kind, buyer_data['kind'])
        self.assertEquals(result.buyer.address_street,  buyer_data['address_street'])
        self.assertEquals(result.buyer.address_number,  buyer_data['address_number'])
        self.assertEquals(result.buyer.address_extra,   buyer_data['address_extra'])
        self.assertEquals(result.buyer.address_city,    buyer_data['address_city'])
        self.assertEquals(result.buyer.address_country, buyer_data['address_country'])
        self.assertEquals(result.buyer.address_zipcode, buyer_data['address_zipcode'])

    def test_retrieving_a_purchase(self):
        other_account = self.create_from_factory(ValidAccountFactory)
        purchase      = self.create_from_factory(ValidPurchaseFactory)

        result = self.service.get_one(purchase.id, by=purchase.customer)
        self.assertEquals(result.id, purchase.id)

        with self.assertRaises(NotAuthorized):
            self.service.get_one(purchase.id, by=other_account)

class PaymentServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(PaymentServiceTestCases, self).setUp()
        self.service = PaymentService()

    def test_retrieves_one_payment_autocasted_to_its_type(self):
        purchase = self.create_from_factory(ValidPurchaseFactory)

        payment           = self.create_from_factory(ValidPaymentFactory, purchase=purchase)
        pagseguro_payment = self.create_from_factory(ValidPagSeguroPaymentFactory, purchase=purchase)

        retrieved = self.service.get_one(purchase.id, payment.id)
        self.assertEquals(retrieved.id, payment.id)
        self.assertEquals(retrieved.__class__, Payment)

        retrieved = self.service.get_one(purchase.id, pagseguro_payment.id)
        self.assertEquals(retrieved.id, pagseguro_payment.id)
        self.assertEquals(retrieved.__class__, PagSeguroPayment)