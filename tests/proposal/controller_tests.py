import sys

import json
import mockito

from werkzeug.exceptions import NotFound

from segue.proposal import ProposalController
from segue.errors import SegueValidationError, NotAuthorized

from support import SegueApiTestCase, hashie
from support.factories import *

class ProposalControllerTestCases(SegueApiTestCase):
    def setUp(self):
        super(ProposalControllerTestCases, self).setUp()
        self.mock_service = self.mock_controller_dep('proposals', 'service')
        self.mock_owner   = self.mock_controller_dep('proposals', 'current_user', ValidAccountFactory.create())

        self.mock_jwt(self.mock_owner)

    def _build_validation_error(self):
        error_1 = hashie(validator='minLength', relative_path=['field']);
        error_2 = hashie(validator='maxLength', relative_path=['other']);
        return SegueValidationError([error_1, error_2])

    def test_invalid_entities_become_422_error(self):
        data = { "arbitrary": "json that will be mocked out anyway" }
        raw_json = json.dumps(data)
        validation_error = self._build_validation_error()
        mockito.when(self.mock_service).create(data, self.mock_owner).thenRaise(validation_error)

        response = self.jpost('/proposals', data=raw_json)
        errors = json.loads(response.data)['errors']

        self.assertEquals(errors[0]['field'], 'field')
        self.assertEquals(errors[1]['field'], 'other')
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

        mockito.when(self.mock_service).modify(123, data, by=self.mock_owner).thenReturn(resulting)

        response = self.jput('/proposals/123', data=raw_json)
        content = json.loads(response.data)['resource']

        mockito.verify(self.mock_service).modify(123, data, by=self.mock_owner)
        self.assertEquals(content['title'], resulting.title)

    def test_modify_proposal_wrong_owner(self):
        data = { "arbitrary": "json that will be mocked out anyway" }
        raw_json = json.dumps(data)
        mockito.when(self.mock_service).check_ownership(123, self.mock_owner).thenReturn(False)
        mockito.when(self.mock_service).modify(123, data, by=self.mock_owner).thenRaise(NotAuthorized)

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

    def test_invite(self):
        data = { "email": "fulano@example.com" }
        raw_json = json.dumps(data)
        mock_invite = ValidInviteFactory.build()
        mockito.when(self.mock_service).check_ownership(123, self.mock_owner).thenReturn(True)
        mockito.when(self.mock_service).invite(123, data).thenReturn(mock_invite)

    def test_invite_answer(self):
        data = { "hash": "12345" }
        raw_json = json.dumps(data)
        mockito.when(self.mock_service).invite_answer(123, 456, data).thenReturn(True)

        response = self.jput('/proposals/123/invite/456', data=raw_json)

        self.assertEquals(response.status_code, 200)
