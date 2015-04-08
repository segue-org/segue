import sys;

import json
import mockito

from segue.caravan import CaravanService
from segue.errors import AccountAlreadyHasCaravan, NotAuthorized, SegueValidationError

from ..support import SegueApiTestCase
from ..support.factories import *

class CaravanServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(CaravanServiceTestCases, self).setUp()
        self.service = CaravanService()
        self.mock_owner = ValidAccountFactory.create()

    def test_cannot_create_invalid_caravan(self):
        data = { "invalid": "data" }
        with self.assertRaises(SegueValidationError):
            self.service.create(data, self.mock_owner)

    def test_creates_upto_one_caravan_and_retrieves_it(self):
        data = ValidCaravanFactory().to_json()

        saved = self.service.create(data, self.mock_owner)
        retrieved = self.service.get_one(saved.id, self.mock_owner)

        self.assertEquals(saved, retrieved)

        with self.assertRaises(AccountAlreadyHasCaravan):
            self.service.create(data, self.mock_owner)

    def test_retrieves_caravan_checking_ownership(self):
        saved = self.create_from_factory(ValidCaravanFactory)

        retrieved = self.service.get_one(saved.id, saved.owner)

        self.assertEquals(saved, retrieved)

        with self.assertRaises(NotAuthorized):
            other_owner = self.create_from_factory(ValidAccountFactory)
            self.service.get_one(saved.id, other_owner)


