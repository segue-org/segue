from contextlib import contextmanager

import json
import mockito

from segue.errors import NotAuthorized

from ..support import SegueApiTestCase
from ..support.factories import *

class AdminControllerFunctionalTestCases(SegueApiTestCase):
    def setUp(self):
        super(AdminControllerFunctionalTestCases, self).setUp()

    @contextmanager
    def normal_user(self):
        mock_user = self.mock_controller_dep('admin', 'current_user', ValidAccountFactory.create())
        self.mock_jwt(mock_user)
        yield mock_user

    @contextmanager
    def admin_user(self):
        mock_user = self.mock_controller_dep('admin', 'current_user', ValidAdminAccountFactory.create())
        self.mock_jwt(mock_user)
        yield mock_user

    def setUpData(self):
        account0 = self.create_from_factory(ValidAccountFactory, id=111, document="1234", name="Ferdinando Ferreira")
        account1 = self.create_from_factory(ValidAccountFactory, id=222, document="4567", name="Astrogildo Nogueira")
        account2 = self.create_from_factory(ValidAccountFactory, id=333, document="7890", name="Pedro Alvarenga")
        account3 = self.create_from_factory(ValidAccountFactory, id=444, document="3451", name="Hermano Neves")

        caravan   = self.create_from_factory(ValidCaravanFactory, owner=account3)
        proposal  = self.create_from_factory(ValidProposalFactory, owner=account3)
        purchase1 = self.create_from_factory(ValidPurchaseFactory, customer=account3)
        purchase2 = self.create_from_factory(ValidPurchaseFactory, customer=account3)
        purchase3 = self.create_from_factory(ValidPurchaseFactory, customer=account3, status='paid')
        payment1  = self.create_from_factory(ValidPaymentFactory, purchase=purchase1)
        payment2  = self.create_from_factory(ValidPaymentFactory, purchase=purchase2)
        payment3  = self.create_from_factory(ValidPaymentFactory, purchase=purchase3)
        payment4  = self.create_from_factory(ValidPaymentFactory, purchase=purchase3, status='paid')
        return locals()

    def test_lookup_payments_by_purchase(self):
        ctx = self.setUpData()
        with self.admin_user():
            response = self.jget('/admin/payments', query_string={"purchase_id": ctx['purchase3'].id})
            items = json.loads(response.data)['items']

            self.assertEquals(response.status_code, 200)
            self.assertEquals(len(items), 2)

    def test_lookup_purchases_by_customer(self):
        ctx = self.setUpData()
        with self.admin_user():
            response = self.jget('/admin/purchases', query_string={"customer_id": ctx['account3'].id})
            items = json.loads(response.data)['items']

            self.assertEquals(response.status_code, 200)
            self.assertEquals(len(items), 3)

    def test_needle_account_denies_access_to_non_admin(self):
        with self.normal_user():
            response = self.jget('/admin/accounts', query_string={"q":"eira"})
            self.assertEquals(response.status_code, 403)

    def test_needle_account_looks_for_name_parts(self):
        ctx = self.setUpData()

        with self.admin_user():
            response = self.jget('/admin/accounts', query_string={"q":"eira"})
            items = json.loads(response.data)['items']

            self.assertEquals(response.status_code, 200)
            self.assertEquals(len(items), 2)
            self.assertEquals(items[0]['document'], "1234")
            self.assertEquals(items[1]['document'], "4567")
            self.assertEquals(items[0]['$type'], 'AccountDetailResponse')
            self.assertEquals(items[1]['$type'], 'AccountDetailResponse')

    def test_needle_account_looks_for_document_parts(self):
        ctx = self.setUpData()

        with self.admin_user():
            response = self.jget('/admin/accounts', query_string={"q":"7890"})
            items = json.loads(response.data)['items']

            self.assertEquals(response.status_code, 200)
            self.assertEquals(len(items), 1)
            self.assertEquals(items[0]['name'], "Pedro Alvarenga")

    def test_needle_account_gives_fully_detailed_responses(self):
        ctx = self.setUpData()

        with self.admin_user():
            response1 = self.jget('/admin/accounts', query_string={"q":"7890"})
            items = json.loads(response1.data)['items']
            response2 = self.jget('/admin/accounts/333')
            item = json.loads(response2.data)['resource']

            self.assertEquals(items[0], item)

    def test_get_account_denies_access_to_non_admin(self):
        with self.normal_user():
            response = self.jget('/admin/accounts/444')
            self.assertEquals(response.status_code, 403)

    def test_get_account_404s_when_account_does_not_exist(self):
        with self.admin_user():
            response = self.jget('/admin/accounts/666')
            self.assertEquals(response.status_code, 404)

    def test_get_account_has_links(self):
        ctx = self.setUpData()

        with self.admin_user():
            response = self.jget('/admin/accounts/444')
            item = json.loads(response.data)['resource']
            links = item['links']

            self.assertEquals(item['$type'], 'AccountDetailResponse')

            self.assertItemsEqual(links.keys(), ["caravans", "payments", "proposals", "purchases"])
            self.assertEquals(links['caravans']['count'],  1)
            self.assertEquals(links['proposals']['count'], 1)
            self.assertEquals(links['payments']['count'],  4)
            self.assertEquals(links['purchases']['count'], 3)



