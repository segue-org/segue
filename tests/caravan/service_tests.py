import sys;

import json
import mockito

from segue.errors import NotAuthorized, SegueValidationError
from segue.caravan.errors import AccountAlreadyHasCaravan
from segue.caravan.services import CaravanService, CaravanInviteService
from segue.caravan.models import CaravanLeaderPurchase

from ..support import SegueApiTestCase
from ..support.factories import *

class CaravanServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(CaravanServiceTestCases, self).setUp()
        self.service = CaravanService()
        self.mock_owner = self.create_from_factory(ValidAccountFactory)

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

    def test_retrieves_caravan_by_owner(self):
        existing = self.create_from_factory(ValidCaravanWithOwnerFactory)

        retrieved = self.service.get_by_owner(existing.owner.id, existing.owner)

        self.assertEquals(existing, retrieved)

        with self.assertRaises(NotAuthorized):
            self.service.get_by_owner(existing.owner.id, self.mock_owner)

    def test_retrieves_caravan_checking_ownership(self):
        existing = self.create_from_factory(ValidCaravanWithOwnerFactory)

        retrieved = self.service.get_one(existing.id, existing.owner)

        self.assertEquals(existing, retrieved)

        with self.assertRaises(NotAuthorized):
            self.service.get_one(existing.id, self.mock_owner)

    def def_test_gives_leader_an_exemption(self):
        caravan = self.create_from_factory(ValidCaravanWithOwnerFactory)

        result = self.service.update_leader_exemption(caravan.id, caravan.owner)
        self.assertEquals(result, None)

        rider1 = self.create_from_factory(ValidCaravanPurchaseFactory, caravan=caravan, status='paid')
        rider2 = self.create_from_factory(ValidCaravanPurchaseFactory, caravan=caravan, status='paid')
        rider3 = self.create_from_factory(ValidCaravanPurchaseFactory, caravan=caravan, status='paid')
        rider4 = self.create_from_factory(ValidCaravanPurchaseFactory, caravan=caravan, status='paid')
        rider5 = self.create_from_factory(ValidCaravanPurchaseFactory, caravan=caravan, status='pending')

        result = self.service.update_leader_exemption(caravan.id, caravan.owner)
        self.assertEquals(result, None)

        rider6 = self.create_from_factory(ValidCaravanPurchaseFactory, caravan=caravan, status='paid')
        result = self.service.update_leader_exemption(caravan.id, caravan.owner)
        self.assertIsInstance(result, CaravanLeaderPurchase)
        self.assertEquals(result.caravan, caravan)
        self.assertEquals(result.status, 'paid')

        rider7 = self.create_from_factory(ValidCaravanPurchaseFactory, caravan=caravan, status='paid')
        result = self.service.update_leader_exemption(caravan.id, caravan.owner)
        self.assertEquals(result, None)

class CaravanInviteServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(CaravanInviteServiceTestCases, self).setUp()
        self.mock_hasher = mockito.Mock()
        self.mock_mailer = mockito.Mock()
        self.mock_owner = ValidAccountFactory.create()

        self.service = CaravanInviteService(hasher=self.mock_hasher, mailer=self.mock_mailer)
        self.caravan = self.create_from_factory(ValidCaravanFactory, owner=self.mock_owner)

    def test_list_valid_owner(self):
        caravan = self.create_from_factory(ValidCaravanFactory, owner=self.mock_owner)
        result = self.service.list(caravan.id, by=self.mock_owner)
        self.assertEquals(result, [])

    def test_list_wrong_owner(self):
        other_owner = ValidAccountFactory.create()
        caravan = self.create_from_factory(ValidCaravanFactory, owner=self.mock_owner)

        with self.assertRaises(NotAuthorized):
            self.service.list(caravan.id, by=other_owner)

    def test_invite_rider(self):
        invite_data = { 'recipient': 'fulano@example.com', 'name': 'Fulano' }
        mockito.when(self.mock_hasher).generate().thenReturn('123ABC')
        mockito.when(self.mock_mailer).caravan_invite(mockito.any())

        invite = self.service.create(self.caravan.id, invite_data, by=self.mock_owner)

        self.assertEquals(invite.hash,      '123ABC')
        self.assertEquals(invite.recipient, invite_data['recipient'])
        self.assertEquals(invite.name,      invite_data['name'])

        mockito.verify(self.mock_mailer).caravan_invite(invite)

    def test_get_by_hash(self):
        invite = self.create_from_factory(ValidCaravanInviteFactory)

        retrieved = self.service.get_by_hash(invite.hash)

        self.assertEquals(retrieved.status, invite.status)
