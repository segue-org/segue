import flask

from controllers import CertificateController

class CertificateBlueprint(flask.Blueprint):
    def __init__(self):
        super(CertificateBlueprint, self).__init__('certificates', __name__, url_prefix='/accounts/<int:account_id>/certificates')
        self.controller = CertificateController()
        self.add_url_rule('', methods=['GET'],  view_func=self.controller.list)
        self.add_url_rule('', methods=['POST'], view_func=self.controller.issue)
