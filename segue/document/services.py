import os.path
import magic

from segue.core import config
from segue.document.errors import DocumentNotFound

class DocumentService(object):
    def __init__(self, override_root=None, magic_impl=None):
        self.override_root = override_root
        self.magic         = magic_impl or magic

    def get_by_hash(self, kind, document_hash):
        root = self.override_root or config.STORAGE_DIR
        filename = "{}-{}".format(kind, document_hash)
        path = os.path.join(root, filename)
        if not os.path.exists(path): raise DocumentNotFound(filename)
        content = open(path,'r').read()
        mimetype = self.magic.from_buffer(content, mime=True)
        return content, mimetype


