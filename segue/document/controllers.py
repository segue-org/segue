from flask import Response

from services import DocumentService

class DocumentController(object):
    def __init__(self, service=None):
        self.service = service or DocumentService()

    def get_by_hash(self, kind=None, document_hash=None):
        content, mimetype = self.service.get_by_hash(kind, document_hash)
        return Response(content, mimetype=mimetype)
