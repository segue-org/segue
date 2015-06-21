import flask
from controllers import DocumentController

class DocumentBlueprint(flask.Blueprint):
    def __init__(self):
        super(DocumentBlueprint, self).__init__('documents', __name__, url_prefix='/documents')
        self.controller = DocumentController()
        self.add_url_rule('/<string:kind>-<string:document_hash>', methods=['GET'], view_func=self.controller.get_by_hash)

