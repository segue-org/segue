import flask

from segue.core import config
from segue.decorators import jsoned, accepts_html

from responses import RoomResponse, SlotResponse, NotificationResponse
from services import RoomService, SlotService, NotificationService

class RoomController(object):
    def __init__(self, service=None):
        self.service = service or RoomService()

    @jsoned
    def get_one(self, room_id):
        result = self.service.get_one(room_id) or flask.abort(404)
        return RoomResponse.create(result), 200

    @jsoned
    def list_all(self):
        result = self.service.query()
        return RoomResponse.create(result), 200

class SlotController(object):
    def __init__(self, service=None):
        self.service = service or SlotService()

    @jsoned
    def of_room(self, room_id):
        result = self.service.of_room(room_id) or flask.abort(404)
        return SlotResponse.create(result, links=False), 200

    @jsoned
    def get_one(self, room_id, slot_id):
        result = self.service.get_one(slot_id) or flask.abort(404)
        return SlotResponse.create(result), 200

class NotificationController(object):
    def __init__(self, service=None):
        self.service = service or NotificationService()

    @jsoned
    @accepts_html
    def get_by_hash(self, hash_code, wants_html=False):
        notification = self.service.get_by_hash(hash_code) or flask.abort(404)
        if wants_html:
            path = '/#/notification/{}/{}/answer'.format(hash_code, notification.kind)
            return flask.redirect(config.FRONTEND_URL + path)
        else:
            return NotificationResponse.create(notification), 200

    @jsoned
    def accept(self, hash_code):
        notification = self.service.accept_notification(hash_code)
        return NotificationResponse.create(notification), 200

    @jsoned
    def decline(self, hash_code):
        notification = self.service.decline_notification(hash_code)
        return NotificationResponse.create(notification), 200
