import flask

from ..proposal import service

class ProposalController(object):
    def __init__(self, service=service):
        self.service = service

    def get_one(self, proposal_id):
        return flask.jsonify(self.service.get_one(proposal_id))


class Blueprint(flask.Blueprint):
    def __init__(self):
        super(Blueprint, self).__init__('products', __name__, url_prefix='/proposal')
        self.controller = ProposalController()
        self.add_url_rule('/<proposal_id>', methods=['GET'], view_func=self.controller.get_one)

