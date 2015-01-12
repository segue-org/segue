import flask

from core import log

from proposal import ProposalController

class ProposalBlueprint(flask.Blueprint):
    def __init__(self):
        super(ProposalBlueprint, self).__init__('proposals', __name__, url_prefix='/proposal')
        self.controller = ProposalController()
        self.add_url_rule('',                      methods=['POST'], view_func=self.controller.create)
        self.add_url_rule('/<int:proposal_id>',    methods=['GET'],  view_func=self.controller.get_one)
        self.add_url_rule('/<string:name>.schema', methods=['GET'],  view_func=self.controller.schema)

class AccountBlueprint(flask.Blueprint):
    def __init__(self):
        super(AccountBlueprint, self).__init__('auth', __name__, url_prefix='/account')

blueprints = [
    ProposalBlueprint(),
    AccountBlueprint()
]
