import flask

from core import log

from proposal import ProposalController

class ProposalBlueprint(flask.Blueprint):
    def __init__(self):
        super(ProposalBlueprint, self).__init__('proposals', __name__, url_prefix='/proposal')
        self.controller = ProposalController()
        self.add_url_rule('',                   methods=['POST'], view_func=self.controller.create)
        self.add_url_rule('/<int:proposal_id>', methods=['GET'],  view_func=self.controller.get_one)

blueprints = [
    ProposalBlueprint()
]
