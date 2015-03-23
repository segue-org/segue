import os.path

import magic
from flask import Response
from segue.core import config
from segue.errors import DocumentNotFound

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


class DocumentController(object):
    def __init__(self, service=None):
        self.service = service or DocumentService()

    def get_by_hash(self, kind=None, document_hash=None):
        content, mimetype = self.service.get_by_hash(kind, document_hash)
        return Response(content, mimetype=mimetype)
