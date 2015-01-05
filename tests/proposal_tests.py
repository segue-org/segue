import json
import mockito

from werkzeug.exceptions import NotFound

from lib.proposal import ProposalService, ProposalController

from lib.core import log

from .factories import ProposalFactory
from . import SegueApiTestCase

class ProposalServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(ProposalServiceTestCases, self).setUp()
        self.service = ProposalService()

    def test_create_and_retrieve(self):
        proposal = ProposalFactory()

        saved = self.service.create(proposal)
        retrieved = self.service.get_one(saved.id)

        self.assertEquals(saved, retrieved)

    def test_non_existing_entity_is_none(self):
        retrieved = self.service.get_one(1234)
        self.assertEquals(retrieved, None)

class ProposalControllerTestCases(SegueApiTestCase):
    def setUp(self):
        super(ProposalControllerTestCases, self).setUp()
        self.service = mockito.Mock()
        self.app.blueprints['proposals'].controller.service = self.service

    def test_404s_on_non_existing_entity(self):
        mockito.when(self.service).get_one(456).thenReturn(None)

        response = self.client.get('/proposal/456')

        self.assertEquals(response.status_code, 404)

    def test_200_on_existing_entity(self):
        mock_proposal = ProposalFactory.build()
        mockito.when(self.service).get_one(123).thenReturn(mock_proposal)

        response = self.client.get('/proposal/123')

        self.assertEquals(response.status_code, 200)

    def test_response_is_json(self):
        mock_proposal = ProposalFactory.build()
        mockito.when(self.service).get_one(123).thenReturn(mock_proposal)

        response = self.client.get('/proposal/123')
        content = json.loads(response.data)['resource']

        self.assertEquals(content['title'],       mock_proposal.title)
        self.assertEquals(content['description'], mock_proposal.description)
        self.assertEquals(content['abstract'],    mock_proposal.abstract)
        self.assertEquals(content['language'],    mock_proposal.language)
        self.assertEquals(content['level'],       mock_proposal.level)
