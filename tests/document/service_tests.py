import os.path
import mockito

from testfixtures import TempDirectory

from segue.document import DocumentService
from segue.errors import DocumentNotFound

from ..support import SegueApiTestCase

class DocumentServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(DocumentServiceTestCases, self).setUp()
        self.root    = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.service = DocumentService(override_root=self.root)

    def test_get_document_by_hash(self):
        content, mimetype = self.service.get_by_hash('boleto','1234.pdf')

        self.assertEquals(mimetype, 'application/pdf')
        self.assertEquals(len(content), 12250)

    def test_raises_error_for_non_existing_documents(self):
        with self.assertRaises(DocumentNotFound):
            self.service.get_by_hash('xixo', '9999.xxx')
