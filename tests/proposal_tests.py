from mockito import *

from lib.proposal import ProposalService, ProposalController

from .factories import ProposalFactory
from . import SegueApiTestCase

class ProposalServiceTestCases(SegueApiTestCase):
    def test_create_and_retrieve(self):
        service = ProposalService()
        proposal = ProposalFactory()

        saved = service.create(proposal)
        retrieved = service.get_one(saved.id)

        self.assertEquals(saved, retrieved)

    def test_non_existing_entity_is_none(self):
        service = ProposalService()

        retrieved = service.get_one(1234)
        self.assertEquals(retrieved, None)
