import sys;

import json
import mockito

from werkzeug.exceptions import NotFound

from segue.proposal import ProposalService, ProposalController, ProposalFactory, Proposal
from segue.errors import SegueValidationError

from support import SegueApiTestCase, hashie
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

    def test_check_ownership(self):
        data = ValidProposalFactory().to_json()
        existing = self.service.create(data, self.mock_owner)
        other_owner = ValidAccountFactory.create()

        positive_case = self.service.check_ownership(existing.id, self.mock_owner)
        negative_case = self.service.check_ownership(existing.id, other_owner)

        self.assertEquals(positive_case, True)
        self.assertEquals(negative_case, False)


    def test_modify_proposal(self):
        data = ValidProposalFactory().to_json()
        existing = self.service.create(data, self.mock_owner)

        new_data = data.copy()
        new_data['title']    = 'ma new title'
        new_data['full']     = 'ma new full'
        new_data['summary']  = 'ma new summ'
        new_data['level']    = 'beginner'
        new_data['language'] = 'pt'
        self.service.modify(existing.id, new_data)

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
