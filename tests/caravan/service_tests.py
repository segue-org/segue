import sys;

import json
import mockito

from segue.caravan import CaravanService

from ..support import SegueApiTestCase
from ..support.factories import *

class CaravanServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(CaravanServiceTestCases, self).setUp()
        self.service = CaravanService()
        self.mock_owner = ValidAccountFactory.create()

    def test_create_and_retrieve_of_valid_proposal(self):
        proposal = ValidCaravanFactory().to_json()

        saved = self.service.create(proposal, self.mock_owner)
        retrieved = self.service.get_one(saved.id)

        self.assertEquals(saved, retrieved)
