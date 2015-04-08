import flask

from proposal import ProposalController, ProposalInviteController
from account import AccountController
from product import ProductController
from purchase import PurchaseController, PaymentController
from document import DocumentController
from caravan import CaravanController, CaravanInviteController

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
        self.add_url_rule('',                             methods=['GET'],   view_func=self.controller.list)
        self.add_url_rule('',                             methods=['POST'],  view_func=self.controller.create)
        self.add_url_rule('/<string:hash_code>',          methods=['GET'],   view_func=self.controller.get_by_hash)
        self.add_url_rule('/<string:hash_code>/accept',   methods=['POST'],  view_func=self.controller.accept)
        self.add_url_rule('/<string:hash_code>/decline',  methods=['POST'],  view_func=self.controller.decline)
        self.add_url_rule('/<string:hash_code>/register', methods=['POST'],  view_func=self.controller.register)

class AccountBlueprint(flask.Blueprint):
    def __init__(self):
        super(AccountBlueprint, self).__init__('accounts', __name__, url_prefix='/accounts')
        self.controller = AccountController()
        self.add_url_rule('',                      methods=['POST'], view_func=self.controller.create)
        self.add_url_rule('/<int:account_id>',     methods=['GET'],  view_func=self.controller.get_one)
        self.add_url_rule('/<int:account_id>',     methods=['PUT'],  view_func=self.controller.modify)
        self.add_url_rule('/<string:name>.schema', methods=['GET'],  view_func=self.controller.schema)
        self.add_url_rule('/<int:account_id>/proposals', methods=['GET'], view_func=self.controller.list_proposals)
        self.add_url_rule('/<int:account_id>/purchases', methods=['GET'], view_func=self.controller.list_purchases)

class ProductBlueprint(flask.Blueprint):
    def __init__(self):
        super(ProductBlueprint, self).__init__('products', __name__, url_prefix='/products')
        self.controller = ProductController()
        self.add_url_rule('',                            methods=['GET'],  view_func=self.controller.list)
        self.add_url_rule('/<int:product_id>/purchase',  methods=['POST'], view_func=self.controller.purchase)
        self.add_url_rule('/caravan/<string:hash_code>', methods=['GET'],  view_func=self.controller.caravan_products)

class PurchaseBlueprint(flask.Blueprint):
    def __init__(self):
        super(PurchaseBlueprint, self).__init__('purchases', __name__, url_prefix='/purchases')
        self.controller = PurchaseController()
        self.add_url_rule('',                                       methods=['GET'],  view_func=self.controller.list)
        self.add_url_rule('/<string:name>.schema',                  methods=['GET'],  view_func=self.controller.schema)
        self.add_url_rule('/<int:purchase_id>',                     methods=['GET'],  view_func=self.controller.get_one)
        self.add_url_rule('/<int:purchase_id>/pay/<string:method>', methods=['POST'], view_func=self.controller.pay)

class PaymentBlueprint(flask.Blueprint):
    def __init__(self):
        super(PaymentBlueprint, self).__init__('purchase_payments', __name__, url_prefix='/purchases/<int:purchase_id>/payments')
        self.controller = PaymentController()
        self.add_url_rule('/<int:payment_id>/notify',   methods=['POST'], view_func=self.controller.notify)
        self.add_url_rule('/<int:payment_id>/conclude', methods=['GET'],  view_func=self.controller.conclude)

class DocumentBlueprint(flask.Blueprint):
    def __init__(self):
        super(DocumentBlueprint, self).__init__('documents', __name__, url_prefix='/documents')
        self.controller = DocumentController()
        self.add_url_rule('/<string:kind>-<string:document_hash>', methods=['GET'], view_func=self.controller.get_by_hash)

class SessionBlueprint(flask.Blueprint):
    def __init__(self):
        super(SessionBlueprint, self).__init__('sessions', __name__, url_prefix='/sessions')
        self.controller = AccountController()
        self.add_url_rule('', methods=['POST'], view_func=self.controller.login)

class CaravanBlueprint(flask.Blueprint):
    def __init__(self):
        super(CaravanBlueprint, self).__init__('caravans', __name__, url_prefix='/caravans')
        self.controller = CaravanController()
        self.add_url_rule('',                      methods=['POST'], view_func=self.controller.create)
        self.add_url_rule('/<int:caravan_id>',     methods=['GET'],  view_func=self.controller.get_one)
        self.add_url_rule('/<string:name>.schema', methods=['GET'],  view_func=self.controller.schema)

class CaravanInviteBluePrint(flask.Blueprint):
    def __init__(self):
        super(CaravanInviteBluePrint, self).__init__('caravan_invites', __name__, url_prefix='/caravans/<int:caravan_id>/invites')
        self.controller = CaravanInviteController()
        self.add_url_rule('',                             methods=['GET'],   view_func=self.controller.list)
        self.add_url_rule('',                             methods=['POST'],  view_func=self.controller.create)
        self.add_url_rule('/<string:hash_code>',          methods=['GET'],   view_func=self.controller.get_by_hash)

blueprints = [
    ProposalBlueprint(),
    ProposalInviteBluePrint(),
    AccountBlueprint(),
    ProductBlueprint(),
    PurchaseBlueprint(),
    PaymentBlueprint(),
    DocumentBlueprint(),
    SessionBlueprint(),
    CaravanBlueprint(),
    CaravanInviteBluePrint()
]
