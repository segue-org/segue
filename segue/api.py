import flask

from account import AccountController
from product import ProductController
from purchase import PurchaseController, PaymentController
from document import DocumentController
from admin import AdminController
from judge import JudgeController, MatchController

from proposal import ProposalBlueprint, ProposalInviteBluePrint
from caravan import CaravanBlueprint, CaravanInviteBluePrint
from schedule import NotificationBlueprint, RoomBlueprint, SlotBlueprint

class AccountBlueprint(flask.Blueprint):
    def __init__(self):
        super(AccountBlueprint, self).__init__('accounts', __name__, url_prefix='/accounts')
        self.controller = AccountController()
        self.add_url_rule('/reset',                methods=['POST'], view_func=self.controller.ask_reset)
        self.add_url_rule('',                      methods=['POST'], view_func=self.controller.create)
        self.add_url_rule('/<string:name>.schema', methods=['GET'],  view_func=self.controller.schema)
        self.add_url_rule('/<int:account_id>',     methods=['GET'],  view_func=self.controller.get_one)
        self.add_url_rule('/<int:account_id>',     methods=['PUT'],  view_func=self.controller.modify)

        self.add_url_rule('/<int:account_id>/proposals', methods=['GET'], view_func=self.controller.list_proposals)
        self.add_url_rule('/<int:account_id>/purchases', methods=['GET'], view_func=self.controller.list_purchases)
        self.add_url_rule('/<int:account_id>/caravan',   methods=['GET'], view_func=self.controller.get_caravan)

        self.add_url_rule('/<int:account_id>/reset/<string:hash_code>', methods=['GET'],  view_func=self.controller.get_reset)
        self.add_url_rule('/<int:account_id>/reset/<string:hash_code>', methods=['POST'], view_func=self.controller.perform_reset)

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
        self.add_url_rule('/<int:purchase_id>/clone',               methods=['POST'], view_func=self.controller.clone)

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

class AdminBlueprint(flask.Blueprint):
    def __init__(self):
        super(AdminBlueprint, self).__init__('admin', __name__, url_prefix='/admin')
        self.controller = AdminController()
        self.add_url_rule('/accounts',    methods=['GET'], view_func=self.controller.list_accounts)
        self.add_url_rule('/proposals',   methods=['GET'], view_func=self.controller.list_proposals)
        self.add_url_rule('/purchases',   methods=['GET'], view_func=self.controller.list_purchases)
        self.add_url_rule('/caravans',    methods=['GET'], view_func=self.controller.list_caravans)
        self.add_url_rule('/payments',    methods=['GET'], view_func=self.controller.list_payments)
        self.add_url_rule('/tournaments', methods=['GET'], view_func=self.controller.list_tournaments)

        self.add_url_rule('/accounts/<int:account_id>', methods=['GET'], view_func=self.controller.get_account)

        self.add_url_rule('/proposals/<int:proposal_id>/invites',                methods=['GET'],    view_func=self.controller.list_proposal_invites)
        self.add_url_rule('/proposals/<int:proposal_id>',                        methods=['GET'],    view_func=self.controller.get_proposal)
        self.add_url_rule('/proposals/<int:proposal_id>/set-track',              methods=['POST'],   view_func=self.controller.change_track_of_proposal)
        self.add_url_rule('/proposals/<int:proposal_id>/tags/<string:tag_name>', methods=['POST'],   view_func=self.controller.add_tag_to_proposal)
        self.add_url_rule('/proposals/<int:proposal_id>/tags/<string:tag_name>', methods=['DELETE'], view_func=self.controller.remove_tag_from_proposal)

        self.add_url_rule('/notifications/call/<string:status>', methods=['GET'], view_func=self.controller.list_call_notification_by_status)

        self.add_url_rule('/tournaments/<int:tournament_id>',           methods=['GET'], view_func=self.controller.get_tournament)
        self.add_url_rule('/tournaments/<int:tournament_id>/standings', methods=['GET'], view_func=self.controller.get_standings)

        self.add_url_rule('/call/<int:tournament_id>/<int:track_id>', methods=['GET'], view_func=self.controller.get_ranking_by_track)

class JudgeBlueprint(flask.Blueprint):
    def __init__(self):
        super(JudgeBlueprint, self).__init__('judges', __name__, url_prefix='/judges')
        self.controller = JudgeController()
        self.add_url_rule('/<string:hash_code>',       methods=['GET'], view_func=self.controller.get_by_hash)
        self.add_url_rule('/<string:hash_code>/match', methods=['GET'], view_func=self.controller.match_for_judge)

class MatchBlueprint(flask.Blueprint):
    def __init__(self):
        super(MatchBlueprint, self).__init__('matches', __name__, url_prefix='/matches')
        self.controller = MatchController()
        self.add_url_rule('/<int:match_id>/vote', methods=['POST'], view_func=self.controller.vote_on_match)

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
    CaravanInviteBluePrint(),
    AdminBlueprint(),
    JudgeBlueprint(),
    MatchBlueprint(),
    RoomBlueprint(),
    SlotBlueprint(),
    NotificationBlueprint()
]
