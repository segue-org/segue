import flask

from admin import AdminController

from document import DocumentBlueprint
from judge import JudgeBlueprint, MatchBlueprint
from purchase import PurchaseBlueprint, PaymentBlueprint
from account import AccountBlueprint, SessionBlueprint
from proposal import ProposalBlueprint, ProposalInviteBluePrint
from product import ProductBlueprint
from caravan import CaravanBlueprint, CaravanInviteBluePrint
from schedule import NotificationBlueprint, RoomBlueprint, SlotBlueprint

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
