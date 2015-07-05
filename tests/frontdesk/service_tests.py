from segue.errors import SegueValidationError

from segue.frontdesk.services import PeopleService

from ..support import SegueApiTestCase
from ..support.factories import *

class PeopleServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(PeopleServiceTestCases, self).setUp()
        self.service = PeopleService()

    def test_patch_person_calls_proper_methods(self):
        purchase = self.create(ValidPurchaseFactory)

        result = self.service.patch(purchase.id, name='fulano novo', by_user=purchase.customer)
        self.assertEqual(result.name, 'fulano novo')

        result = self.service.patch(purchase.id, category='hacker', by_user=purchase.customer)
        self.assertEqual(result.category, purchase.product.category)

    def test_patch_person_runs_schema_validation(self):
        purchase = self.create(ValidPurchaseFactory)

        with self.assertRaises(SegueValidationError):
            result = self.service.patch(purchase.id, name='', by_user=purchase.customer)
            self.assertEqual(result.name, 'fulano novo')

