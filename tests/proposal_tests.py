import json
import mockito

from werkzeug.exceptions import NotFound

from segue.proposal import ProposalService, ProposalController, ProposalFactory, Proposal
from segue.errors import SegueValidationError

from support import SegueApiTestCase, ValidProposalFactory, InvalidProposalFactory

class ProposalServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(ProposalServiceTestCases, self).setUp()
        self.service = ProposalService()

    def test_invalid_proposal_raises_validation_error(self):
        proposal = InvalidProposalFactory().to_json()

        with self.assertRaises(SegueValidationError):
            self.service.create(proposal)

    def test_create_and_retrieve_of_valid_proposal(self):
        proposal = ValidProposalFactory().to_json()

        saved = self.service.create(proposal)
        retrieved = self.service.get_one(saved.id)

        self.assertEquals(saved, retrieved)

    def test_non_existing_entity_is_none(self):
        retrieved = self.service.get_one(1234)
        self.assertEquals(retrieved, None)

class ProposalControllerTestCases(SegueApiTestCase):
    def setUp(self):
        super(ProposalControllerTestCases, self).setUp()
        self.mock_service = self.mock_controller_dep('proposals', 'service')

    def test_invalid_entities_become_400_error(self):
        data = { "arbitrary": "json that will be mocked out anyway" }
        raw_json = json.dumps(data)
        mockito.when(self.mock_service).create(data).thenRaise(SegueValidationError([]))

        response = self.jpost('/proposal', data=raw_json)

        self.assertEquals(response.status_code, 400)

    def test_json_input_is_sent_to_service_for_creation(self):
        data = { "arbitrary": "json that will be mocked out anyway" }
        raw_json = json.dumps(data)
        mockito.when(self.mock_service).create(data).thenReturn('bla')

        response = self.jpost('/proposal', data=raw_json)

        mockito.verify(self.mock_service).create(data)
        self.assertEquals(response.status_code, 201)

    def test_404s_on_non_existing_entity(self):
        mockito.when(self.mock_service).get_one(456).thenReturn(None)

        response = self.jget('/proposal/456')

        self.assertEquals(response.status_code, 404)

    def test_200_on_existing_entity(self):
        mock_proposal = ValidProposalFactory.build()
        mockito.when(self.mock_service).get_one(123).thenReturn(mock_proposal)

        response = self.jget('/proposal/123')

        self.assertEquals(response.status_code, 200)

    def test_response_is_json(self):
        mock_proposal = ValidProposalFactory.build()
        mockito.when(self.mock_service).get_one(123).thenReturn(mock_proposal)

        response = self.jget('/proposal/123')
        content = json.loads(response.data)['resource']

        self.assertEquals(content['title'],       mock_proposal.title)
        self.assertEquals(content['description'], mock_proposal.description)
        self.assertEquals(content['abstract'],    mock_proposal.abstract)
        self.assertEquals(content['language'],    mock_proposal.language)
        self.assertEquals(content['level'],       mock_proposal.level)
