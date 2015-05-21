import sys;

import json
import mockito

from segue.errors import AccountAlreadyHasCorporate, NotAuthorized, SegueValidationError
from segue.corporate.services import CorporateService
from segue.corporate.models import CorporatePurchase

from ..support import SegueApiTestCase
from ..support.factories import *

class CorporateServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(CorporateServiceTestCases, self).setUp()
        self.service = CorporateService()
        self.mock_owner = self.create_from_factory(ValidAccountFactory)

    def test_cannot_create_invalid_corporate(self):
        data = { "invalid": "data" }
        with self.assertRaises(SegueValidationError):
            self.service.create(data, self.mock_owner)

    def test_creates_upto_one_corporate_and_retrieves_it(self):
        data = ValidCorporateFactory().to_json()

        saved = self.service.create(data, self.mock_owner)
        retrieved = self.service.get_one(saved.id, self.mock_owner)

        self.assertEquals(saved, retrieved)

        with self.assertRaises(AccountAlreadyHasCorporate):
            self.service.create(data, self.mock_owner)

    def test_retrieves_corporate_by_owner(self):
        existing = self.create_from_factory(ValidCorporateWithOwnerFactory)

        retrieved = self.service.get_by_owner(existing.owner.id, existing.owner)

        self.assertEquals(existing, retrieved)

        with self.assertRaises(NotAuthorized):
            self.service.get_by_owner(existing.owner.id, self.mock_owner)

    def test_retrieves_coroporate_checking_ownership(self):
        existing = self.create_from_factory(ValidCorporateWithOwnerFactory)

        retrieved = self.service.get_one(existing.id, existing.owner)

        self.assertEquals(existing, retrieved)

        with self.assertRaises(NotAuthorized):
            self.service.get_one(existing.id, self.mock_owner)
