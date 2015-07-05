import flask
from controllers import *

from responses import *

class AdminAccountBlueprint(flask.Blueprint):
    def __init__(self):
        super(AdminAccountBlueprint, self).__init__('admin.account', __name__, url_prefix='/admin/accounts')
        self.controller = AdminAccountController()
        self.add_url_rule('',                                 methods=['GET'],  view_func=self.controller.list)
        self.add_url_rule('',                                 methods=['POST'], view_func=self.controller.create)
        self.add_url_rule('/<int:account_id>',                methods=['GET'],  view_func=self.controller.get_one)
        self.add_url_rule('/<int:account_id>',                methods=['PUT'],  view_func=self.controller.modify)
        self.add_url_rule('/<int:account_id>/proposals',      methods=['GET'],  view_func=self.controller.proposals_of_account)
        self.add_url_rule('/holder-of/<int:purchase_id>',     methods=['GET'],  view_func=self.controller.get_by_purchase)

class AdminProposalBlueprint(flask.Blueprint):
    def __init__(self):
        super(AdminProposalBlueprint, self).__init__('admin.proposal', __name__, url_prefix='/admin/proposals')
        self.controller = AdminProposalController()
        self.add_url_rule('',                                          methods=['GET'],    view_func=self.controller.list)
        self.add_url_rule('',                                          methods=['POST'],   view_func=self.controller.create)
        self.add_url_rule('/<int:proposal_id>',                        methods=['GET'],    view_func=self.controller.get_one)
        self.add_url_rule('/<int:proposal_id>',                        methods=['PUT'],    view_func=self.controller.modify)
        self.add_url_rule('/<int:proposal_id>/invites',                methods=['GET'],    view_func=self.controller.list_invites)
        self.add_url_rule('/<int:proposal_id>/coauthors',              methods=['POST'],   view_func=self.controller.set_coauthors)
        self.add_url_rule('/<int:proposal_id>/status',                 methods=['POST'],   view_func=self.controller.set_status)
        self.add_url_rule('/<int:proposal_id>/set-track',              methods=['POST'],   view_func=self.controller.change_track)
        self.add_url_rule('/<int:proposal_id>/tags/<string:tag_name>', methods=['POST'],   view_func=self.controller.add_tag)
        self.add_url_rule('/<int:proposal_id>/tags/<string:tag_name>', methods=['DELETE'], view_func=self.controller.remove_tag)

class AdminPromoCodeBlueprint(flask.Blueprint):
    def __init__(self):
        super(AdminPromoCodeBlueprint, self).__init__('admin.promocodes', __name__, url_prefix="/admin/promocodes")
        self.controller = AdminPromoCodeController()
        self.add_url_rule('',                    methods=['GET'],  view_func=self.controller.list_promocodes)
        self.add_url_rule('',                    methods=['POST'], view_func=self.controller.create)
        self.add_url_rule('/<int:promocode_id>', methods=['GET'],  view_func=self.controller.get_one)
        self.add_url_rule('/products',           methods=['GET'],  view_func=self.controller.get_products)

class AdminTournamentsBlueprint(flask.Blueprint):
    def __init__(self):
        super(AdminTournamentsBlueprint, self).__init__('admin.tournaments', __name__, url_prefix="/admin/tournaments")
        self.controller = AdminJudgeController()
        self.add_url_rule('',                               methods=['GET'], view_func=self.controller.list_tournaments)
        self.add_url_rule('/<int:tournament_id>',           methods=['GET'], view_func=self.controller.get_tournament)
        self.add_url_rule('/<int:tournament_id>/standings', methods=['GET'], view_func=self.controller.get_standings)

class AdminCallBlueprint(flask.Blueprint):
    def __init__(self):
        super(AdminCallBlueprint, self).__init__('admin.call', __name__, url_prefix="/admin/call")
        self.controller = AdminJudgeController()
        self.add_url_rule('/<int:tournament_id>/<int:track_id>',   methods=['GET'], view_func=self.controller.get_ranking_by_track)

class AdminRoomBlueprint(flask.Blueprint):
    def __init__(self):
        super(AdminRoomBlueprint, self).__init__('admin.room', __name__, url_prefix="/admin/rooms")
        self.controller = AdminScheduleController()
        self.add_url_rule('', methods=['GET'], view_func=self.controller.list_rooms)

class AdminSlotBlueprint(flask.Blueprint):
    def __init__(self):
        super(AdminSlotBlueprint, self).__init__('admin.slot', __name__, url_prefix="/admin/slots")
        self.controller = AdminScheduleController()
        self.add_url_rule('',                          methods=['GET'],    view_func=self.controller.query_slots)
        self.add_url_rule('/situation',                methods=['GET'],    view_func=self.controller.overall_situation)
        self.add_url_rule('/<int:slot_id>',            methods=['GET'],    view_func=self.controller.get_slot)
        self.add_url_rule('/<int:slot_id>/status',     methods=['POST'],   view_func=self.controller.set_status)
        self.add_url_rule('/<int:slot_id>/block',      methods=['POST'],   view_func=self.controller.block_slot)
        self.add_url_rule('/<int:slot_id>/stretch',    methods=['POST'],   view_func=self.controller.stretch_slot)
        self.add_url_rule('/<int:slot_id>/unstretch',  methods=['POST'],   view_func=self.controller.unstretch_slot)
        self.add_url_rule('/<int:slot_id>/unblock',    methods=['POST'],   view_func=self.controller.unblock_slot)
        self.add_url_rule('/<int:slot_id>/talk',       methods=['POST'],   view_func=self.controller.set_talk)
        self.add_url_rule('/<int:slot_id>/talk',       methods=['DELETE'], view_func=self.controller.empty_slot)
        self.add_url_rule('/<int:slot_id>/annotation', methods=['POST'],   view_func=self.controller.annotate_slot)

class AdminBlueprint(flask.Blueprint):
    def __init__(self):
        super(AdminBlueprint, self).__init__('admin', __name__, url_prefix='/admin')
        self.controller = AdminController()
        self.add_url_rule('/purchases',   methods=['GET'], view_func=self.controller.list_purchases)
        self.add_url_rule('/caravans',    methods=['GET'], view_func=self.controller.list_caravans)
        self.add_url_rule('/payments',    methods=['GET'], view_func=self.controller.list_payments)

        self.add_url_rule('/notifications/call/<string:status>', methods=['GET'], view_func=self.controller.list_call_notification_by_status)


def load_blueprints():
    return [
        AdminAccountBlueprint(),
        AdminProposalBlueprint(),
        AdminTournamentsBlueprint(),
        AdminPromoCodeBlueprint(),
        AdminCallBlueprint(),
        AdminRoomBlueprint(),
        AdminSlotBlueprint(),
        AdminBlueprint()
    ]
