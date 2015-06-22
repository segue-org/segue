import flask
from controllers import *

from responses import *

class AdminAccountBlueprint(flask.Blueprint):
    def __init__(self):
        super(AdminAccountBlueprint, self).__init__('admin.account', __name__, url_prefix='/admin/accounts')
        self.controller = AdminAccountController()
        self.add_url_rule('',                  methods=['GET'], view_func=self.controller.list)
        self.add_url_rule('/<int:account_id>', methods=['GET'], view_func=self.controller.get_one)

class AdminProposalBlueprint(flask.Blueprint):
    def __init__(self):
        super(AdminProposalBlueprint, self).__init__('admin.proposal', __name__, url_prefix='/admin/proposals')
        self.controller = AdminProposalController()
        self.add_url_rule('',                                          methods=['GET'], view_func=self.controller.list)
        self.add_url_rule('/<int:proposal_id>/invites',                methods=['GET'],    view_func=self.controller.list_invites)
        self.add_url_rule('/<int:proposal_id>',                        methods=['GET'],    view_func=self.controller.get_one)
        self.add_url_rule('/<int:proposal_id>/set-track',              methods=['POST'],   view_func=self.controller.change_track)
        self.add_url_rule('/<int:proposal_id>/tags/<string:tag_name>', methods=['POST'],   view_func=self.controller.add_tag)
        self.add_url_rule('/<int:proposal_id>/tags/<string:tag_name>', methods=['DELETE'], view_func=self.controller.remove_tag)

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
        self.add_url_rule('',                       methods=['GET'],  view_func=self.controller.query_slots)
        self.add_url_rule('/<int:slot_id>',         methods=['GET'],  view_func=self.controller.get_slot)
        self.add_url_rule('/<int:slot_id>/block',   methods=['POST'], view_func=self.controller.block_slot)
        self.add_url_rule('/<int:slot_id>/unblock', methods=['POST'], view_func=self.controller.unblock_slot)

class AdminBlueprint(flask.Blueprint):
    def __init__(self):
        super(AdminBlueprint, self).__init__('admin', __name__, url_prefix='/admin')
        self.controller = AdminController()
        self.add_url_rule('/purchases',   methods=['GET'], view_func=self.controller.list_purchases)
        self.add_url_rule('/caravans',    methods=['GET'], view_func=self.controller.list_caravans)
        self.add_url_rule('/payments',    methods=['GET'], view_func=self.controller.list_payments)

        self.add_url_rule('/notifications/call/<string:status>', methods=['GET'], view_func=self.controller.list_call_notification_by_status)


blueprints = [
    AdminAccountBlueprint(),
    AdminProposalBlueprint(),
    AdminTournamentsBlueprint(),
    AdminCallBlueprint(),
    AdminRoomBlueprint(),
    AdminSlotBlueprint(),
    AdminBlueprint()
]
