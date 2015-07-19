import os.path
import mockito

from testfixtures import TempDirectory

from segue.document.services import DocumentService
from segue.document.errors import DocumentNotFound

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

    def test_list_all_files_for_kind(self):
        result = self.service.all_files_with_kind('boleto')

        self.assertEquals(len(result), 2)
        self.assertEquals(result[0], 'boleto-1234.pdf')
        self.assertEquals(result[1], 'boleto-ABCD.pdf')

        result = self.service.all_files_with_kind('certificate')
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0], 'certificate-5678.pdf')
