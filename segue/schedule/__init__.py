import flask
from controllers import NotificationController, RoomController, SlotController

class NotificationBlueprint(flask.Blueprint):
    def __init__(self):
        super(NotificationBlueprint, self).__init__('notifications', __name__, url_prefix='/notifications')
        self.controller = NotificationController()
        self.add_url_rule('/<string:hash_code>',         methods=['GET'],  view_func=self.controller.get_by_hash)
        self.add_url_rule('/<string:hash_code>/accept',  methods=['POST'], view_func=self.controller.accept)
        self.add_url_rule('/<string:hash_code>/decline', methods=['POST'], view_func=self.controller.decline)

class RoomBlueprint(flask.Blueprint):
    def __init__(self):
        super(RoomBlueprint, self).__init__('rooms', __name__, url_prefix='/rooms')
        self.controller = RoomController()
        self.add_url_rule('',                     methods=['GET'], view_func=self.controller.list_all)
        self.add_url_rule('/<int:room_id>',       methods=['GET'], view_func=self.controller.get_one)

class SlotBlueprint(flask.Blueprint):
    def __init__(self):
        super(SlotBlueprint, self).__init__('slots', __name__, url_prefix='/rooms/<int:room_id>/slots')
        self.controller = SlotController()
        self.add_url_rule('',               methods=['GET'], view_func=self.controller.of_room)
        self.add_url_rule('/<int:slot_id>', methods=['GET'], view_func=self.controller.get_one)


