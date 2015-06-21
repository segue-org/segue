import mockito

from segue.document.errors import DocumentNotFound
from ..support import SegueApiTestCase

class DocumentControllerTestCases(SegueApiTestCase):
    def setUp(self):
        super(DocumentControllerTestCases, self).setUp()
        self.mock_service = self.mock_controller_dep('documents', 'service')

    def test_get_document_by_hash(self):
        mockito.when(self.mock_service) \
               .get_by_hash('boleto', '1234.pdf') \
               .thenReturn(['le-content', 'application/pdf'])

        response = self.client.get('/documents/boleto-1234.pdf')

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.headers['Content-Type'], 'application/pdf')

    def test_404s_for_invalid_documents(self):
        mockito.when(self.mock_service).get_by_hash('xixo','999.xxx').thenRaise(DocumentNotFound)

        response = self.client.get('/documents/xixo-999.xxx')

        self.assertEquals(response.status_code, 404)
