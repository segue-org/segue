import flask

from proposal import ProposalController

class ProposalBlueprint(flask.Blueprint):
    def __init__(self):
        super(ProposalBlueprint, self).__init__('products', __name__, url_prefix='/proposal')
        self.controller = ProposalController()
        self.add_url_rule('/<proposal_id>', methods=['GET'], view_func=self.controller.get_one)

blueprints = [
    ProposalBlueprint()
]
