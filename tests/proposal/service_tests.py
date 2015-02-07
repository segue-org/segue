import sys;

import json

from segue.proposal import ProposalService
from segue.errors import SegueValidationError, NotAuthorized

from support import SegueApiTestCase
from support.factories import *

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
        data = ValidProposalFactory().to_json()
        existing = self.service.create(data, self.mock_owner)

        new_data = data.copy()
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
        data = ValidProposalFactory().to_json()
        new_data = { 'title': 'ma new title' }
        existing = self.service.create(data, self.mock_owner)

        with self.assertRaises(NotAuthorized):
            self.service.modify(existing.id, new_data, by=other_owner)

        retrieved = self.service.get_one(existing.id)
        self.assertNotEquals(retrieved.title,    'ma new title')
