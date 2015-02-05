import sys;

import json
import mockito

from werkzeug.exceptions import NotFound

from segue.proposal import ProposalService, ProposalController, ProposalFactory, Proposal
from segue.errors import SegueValidationError

from support import SegueApiTestCase
from support import ValidProposalFactory, ValidProposalWithOwnerFactory, InvalidProposalFactory, ValidAccountFactory
from support import hashie

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

class ProposalControllerTestCases(SegueApiTestCase):
    def setUp(self):
        super(ProposalControllerTestCases, self).setUp()
        self.mock_service = self.mock_controller_dep('proposals', 'service')
        self.mock_owner   = self.mock_controller_dep('proposals', 'current_user', ValidAccountFactory.create())

        self.mock_jwt(self.mock_owner)

    def _build_validation_error(self):
        error_1 = hashie(message="m1", schema_path=["1","2"])
        error_2 = hashie(message="m2", schema_path=["3","4"])

        return SegueValidationError([error_1, error_2])

    def test_invalid_entities_become_422_error(self):
        data = { "arbitrary": "json that will be mocked out anyway" }
        raw_json = json.dumps(data)
        validation_error = self._build_validation_error()
        mockito.when(self.mock_service).create(data, self.mock_owner).thenRaise(validation_error)

        response = self.jpost('/proposals', data=raw_json)
        errors = json.loads(response.data)['errors']

        self.assertEquals(errors['1.2'], 'm1')
        self.assertEquals(errors['3.4'], 'm2')
        self.assertEquals(response.status_code, 422)
        self.assertEquals(response.content_type, 'application/json')

    def test_json_input_is_sent_to_service_for_creation(self):
        data = { "arbitrary": "json that will be mocked out anyway" }
        raw_json = json.dumps(data)
        mockito.when(self.mock_service).create(data, self.mock_owner).thenReturn('bla')

        response = self.jpost('/proposals', data=raw_json)

        mockito.verify(self.mock_service).create(data, self.mock_owner)
        self.assertEquals(response.status_code, 201)

    def test_404s_on_non_existing_entity(self):
        mockito.when(self.mock_service).get_one(456).thenReturn(None)

        response = self.jget('/proposals/456')

        self.assertEquals(response.status_code, 404)

    def test_200_on_existing_entity(self):
        mock_proposal = ValidProposalFactory.build()
        mockito.when(self.mock_service).get_one(123).thenReturn(mock_proposal)

        response = self.jget('/proposals/123')

        self.assertEquals(response.status_code, 200)

    def test_response_is_json(self):
        mock_proposal = ValidProposalWithOwnerFactory.create()
        mockito.when(self.mock_service).get_one(123).thenReturn(mock_proposal)

        response = self.jget('/proposals/123')
        content = json.loads(response.data)['resource']

        self.assertEquals(content['title'],    mock_proposal.title)
        self.assertEquals(content['full'],     mock_proposal.full)
        self.assertEquals(content['summary'],  mock_proposal.summary)
        self.assertEquals(content['language'], mock_proposal.language)
        self.assertEquals(content['level'],    mock_proposal.level)
        self.assertNotIn('email', content['owner'].keys())
        self.assertNotIn('role',  content['owner'].keys())

    def test_modify_proposal(self):
        data = { "arbitrary": "json that will be mocked out anyway" }
        raw_json = json.dumps(data)
        existing = ValidProposalFactory.build(owner = ValidAccountFactory.create())
        resulting = ValidProposalFactory.build()

        mockito.when(self.mock_service).check_ownership(123, self.mock_owner).thenReturn(True)
        mockito.when(self.mock_service).modify(123, data).thenReturn(resulting)

        response = self.jput('/proposals/123', data=raw_json)
        content = json.loads(response.data)['resource']

        mockito.verify(self.mock_service).modify(123, data)
        self.assertEquals(content['title'], resulting.title)

    def test_modify_proposal_wrong_owner(self):
        data = { "arbitrary": "json that will be mocked out anyway" }
        raw_json = json.dumps(data)
        mockito.when(self.mock_service).check_ownership(123, self.mock_owner).thenReturn(False)

        response = self.jput('/proposals/123', data=raw_json)

        self.assertEquals(response.status_code, 403)

    def test_list_proposals(self):
        prop1 = ValidProposalFactory.build()
        prop2 = ValidProposalFactory.build()

        mockito.when(self.mock_service).query().thenReturn([prop1, prop2])

        response = self.jget('/proposals')
        items = json.loads(response.data)['items']

        self.assertEquals(len(items), 2)
        self.assertEquals(items[0]['title'], prop1.title)
        self.assertEquals(items[1]['title'], prop2.title)

    def test_list_proposals_with_whitelisted_columns_as_filters(self):
        prop1 = ValidProposalFactory.build()

        mockito.when(self.mock_service).query(owner_id=u'123').thenReturn([prop1])

        response = self.jget('/proposals', query_string={'xonga': u'123', 'owner_id': u'123'})
        items = json.loads(response.data)['items']

        self.assertEquals(len(items), 1)
        self.assertEquals(items[0]['title'], prop1.title)
