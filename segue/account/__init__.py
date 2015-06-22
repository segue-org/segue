import flask

from controllers import AccountController
from admin import AdminAccountController

class AdminAccountBlueprint(flask.Blueprint):
    def __init__(self):
        super(AdminAccountBlueprint, self).__init__('admin.account', __name__, url_prefix='/admin/accounts')
        self.controller = AdminAccountController()
        self.add_url_rule('',                  methods=['GET'], view_func=self.controller.list)
        self.add_url_rule('/<int:account_id>', methods=['GET'], view_func=self.controller.get_one)

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

class SessionBlueprint(flask.Blueprint):
    def __init__(self):
        super(SessionBlueprint, self).__init__('sessions', __name__, url_prefix='/sessions')
        self.controller = AccountController()
        self.add_url_rule('', methods=['POST'], view_func=self.controller.login)
