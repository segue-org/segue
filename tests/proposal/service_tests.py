import sys;

import json
import mockito

from segue.proposal import ProposalService, InviteService
from segue.errors import SegueValidationError, NotAuthorized

from ..support import SegueApiTestCase
from ..support.factories import *

class ProposalServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(ProposalServiceTestCases, self).setUp()
        self.service = ProposalService()
        self.mock_owner = ValidAccountFactory.create()

    def test_invalid_proposal_raises_validation_error(self):
        proposal = InvalidProposalFactory().to_json()

        with self.assertRaises(SegueValidationError):
            self.service.create(proposal, self.mock_owner)

    def test_create_and_retrieve_of_valid_proposal(self):
        proposal = ValidProposalFactory().to_json()

        saved = self.service.create(proposal, self.mock_owner)
        retrieved = self.service.get_one(saved.id)

        self.assertEquals(saved, retrieved)

    def test_non_existing_entity_is_none(self):
        retrieved = self.service.get_one(1234)
        self.assertEquals(retrieved, None)

    def test_modify_proposal_valid_owner(self):
        existing = self.create_from_factory(ValidProposalFactory, owner=self.mock_owner)

        new_data = {}
        new_data['title']    = 'ma new title'
        new_data['full']     = 'ma new full'
        new_data['summary']  = 'ma new summ'
        new_data['level']    = 'beginner'
        new_data['language'] = 'pt'
        self.service.modify(existing.id, new_data, by=self.mock_owner)

        retrieved = self.service.get_one(existing.id)
        self.assertEquals(retrieved.title,    'ma new title')
        self.assertEquals(retrieved.full,     'ma new full')
        self.assertEquals(retrieved.summary,  'ma new summ')
        self.assertEquals(retrieved.level,    'beginner')
        self.assertEquals(retrieved.language, 'pt')

        # changing owner is a special case, and can't be done by mass update
        self.assertEquals(retrieved.owner, existing.owner)
        # id should never change
        self.assertEquals(retrieved.id,    existing.id)

    def test_modify_proposal_wrong_owner(self):
        other_owner = ValidAccountFactory.create()
        existing = self.create_from_factory(ValidProposalFactory, owner=self.mock_owner)

        with self.assertRaises(NotAuthorized):
            new_data = { 'title': 'ma new title' }
            self.service.modify(existing.id, new_data, by=other_owner)

        retrieved = self.service.get_one(existing.id)
        self.assertNotEquals(retrieved.title, 'ma new title')

class InviteServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(InviteServiceTestCases, self).setUp()
        self.mock_owner = ValidAccountFactory.create()
        self.service = InviteService()
        self.proposal = self.create_from_factory(ValidProposalFactory, owner=self.mock_owner)

    def test_list_valid_owner(self):
        proposal = self.create_from_factory(ValidProposalFactory, owner=self.mock_owner)
        result = self.service.list(proposal.id, by=self.mock_owner)
        self.assertEquals(result, [])

    def test_list_wrong_owner(self):
        other_owner = ValidAccountFactory.create()
        proposal = self.create_from_factory(ValidProposalFactory, owner=self.mock_owner)

        with self.assertRaises(NotAuthorized):
            self.service.list(proposal.id, by=other_owner)

    def test_invite_coauthor(self):
        invite_data = { 'recipient': 'fulano@example.com', 'name': 'Fulano' }

        result = self.service.create(self.proposal.id, invite_data, by=self.mock_owner)

        self.assertEquals(result.recipient, invite_data['recipient'])
        self.assertEquals(result.name,      invite_data['name'])

    def test_decline(self):
        invite = self.create_from_factory(ValidInviteFactory)
        result = self.service.decline(invite.hash)
        retrieved = self.service.get_by_hash(invite.hash)
        self.assertEquals(retrieved.status, 'declined')


