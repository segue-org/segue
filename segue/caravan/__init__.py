import flask

from controllers import CaravanInviteController, CaravanController

class CaravanBlueprint(flask.Blueprint):
    def __init__(self):
        super(CaravanBlueprint, self).__init__('caravans', __name__, url_prefix='/caravans')
        self.controller = CaravanController()
        self.add_url_rule('',                      methods=['POST'], view_func=self.controller.create)
        self.add_url_rule('',                      methods=['GET'],  view_func=self.controller.get_one)
        self.add_url_rule('/<int:caravan_id>',     methods=['PUT'],  view_func=self.controller.modify)
        self.add_url_rule('/<int:caravan_id>',     methods=['GET'],  view_func=self.controller.get_one)
        self.add_url_rule('/<string:name>.schema', methods=['GET'],  view_func=self.controller.schema)

class CaravanInviteBluePrint(flask.Blueprint):
    def __init__(self):
        super(CaravanInviteBluePrint, self).__init__('caravan_invites', __name__, url_prefix='/caravans/<int:caravan_id>/invites')
        self.controller = CaravanInviteController()
        self.add_url_rule('',                             methods=['GET'],   view_func=self.controller.list)
        self.add_url_rule('',                             methods=['POST'],  view_func=self.controller.create)
        self.add_url_rule('/<string:hash_code>',          methods=['GET'],   view_func=self.controller.get_by_hash)
        self.add_url_rule('/<string:hash_code>/accept',   methods=['POST'],  view_func=self.controller.accept)
        self.add_url_rule('/<string:hash_code>/decline',  methods=['POST'],  view_func=self.controller.decline)
        self.add_url_rule('/<string:hash_code>/register', methods=['POST'],  view_func=self.controller.register)



