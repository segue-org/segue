import flask

from proposal import ProposalController, ProposalInviteController
from account import AccountController
from product import ProductController
from purchase import PurchaseController

class ProposalBlueprint(flask.Blueprint):
    def __init__(self):
        super(ProposalBlueprint, self).__init__('proposals', __name__, url_prefix='/proposals')
        self.controller = ProposalController()
        self.add_url_rule('',                      methods=['POST'], view_func=self.controller.create)
        self.add_url_rule('',                      methods=['GET'],  view_func=self.controller.list)
        self.add_url_rule('/<int:proposal_id>',    methods=['GET'],  view_func=self.controller.get_one)
        self.add_url_rule('/<int:proposal_id>',    methods=['PUT'],  view_func=self.controller.modify)
        self.add_url_rule('/<string:name>.schema', methods=['GET'],  view_func=self.controller.schema)
        self.add_url_rule('/tracks',               methods=['GET'],  view_func=self.controller.list_tracks)

class ProposalInviteBluePrint(flask.Blueprint):
    def __init__(self):
        super(ProposalInviteBluePrint, self).__init__('proposal_invites', __name__, url_prefix='/proposals/<int:proposal_id>/invites')
        self.controller = ProposalInviteController()
        self.add_url_rule('',                        methods=['GET'],   view_func=self.controller.list)
        self.add_url_rule('',                        methods=['POST'],  view_func=self.controller.create)
        self.add_url_rule('/<string:hash>',          methods=['GET'],   view_func=self.controller.get_by_hash)
        self.add_url_rule('/<string:hash>/accept',   methods=['POST'],  view_func=self.controller.accept)
        self.add_url_rule('/<string:hash>/decline',  methods=['POST'],  view_func=self.controller.decline)
        self.add_url_rule('/<string:hash>/register', methods=['POST'],  view_func=self.controller.register)

class AccountBlueprint(flask.Blueprint):
    def __init__(self):
        super(AccountBlueprint, self).__init__('accounts', __name__, url_prefix='/accounts')
        self.controller = AccountController()
        self.add_url_rule('',                      methods=['POST'], view_func=self.controller.create)
        self.add_url_rule('/<int:account_id>',     methods=['GET'],  view_func=self.controller.get_one)
        self.add_url_rule('/<int:account_id>',     methods=['PUT'],  view_func=self.controller.modify)
        self.add_url_rule('/<string:name>.schema', methods=['GET'],  view_func=self.controller.schema)
        self.add_url_rule('/<int:account_id>/proposals', methods=['GET'], view_func=self.controller.list_proposals)

class ProductBlueprint(flask.Blueprint):
    def __init__(self):
        super(ProductBlueprint, self).__init__('products', __name__, url_prefix='/products')
        self.controller = ProductController()
        self.add_url_rule('',                           methods=['GET'],  view_func=self.controller.list)
        self.add_url_rule('/<int:product_id>/purchase', methods=['POST'], view_func=self.controller.purchase)
        self.add_url_rule('/<string:name>.schema',      methods=['GET'],  view_func=self.controller.schema)

class PurchaseBlueprint(flask.Blueprint):
    def __init__(self):
        super(PurchaseBlueprint, self).__init__('purchases', __name__, url_prefix='/purchases')
        self.controller = PurchaseController()
        self.add_url_rule('',                       methods=['GET'],  view_func=self.controller.list)
        self.add_url_rule('/<int:purchase_id>',     methods=['GET'],  view_func=self.controller.get_one)
        self.add_url_rule('/<int:purchase_id>/pay', methods=['POST'], view_func=self.controller.pay)
        self.add_url_rule('/notify',                methods=['POST'], view_func=self.controller.notify)

class SessionBlueprint(flask.Blueprint):
    def __init__(self):
        super(SessionBlueprint, self).__init__('sessions', __name__, url_prefix='/sessions')
        self.controller = AccountController()
        self.add_url_rule('', methods=['POST'], view_func=self.controller.login)

blueprints = [
    ProposalBlueprint(),
    ProposalInviteBluePrint(),
    AccountBlueprint(),
    ProductBlueprint(),
    PurchaseBlueprint(),
    SessionBlueprint()
]
