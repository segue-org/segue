import flask

from segue.json import jsoned

from responses import RoomResponse, SlotResponse
from services import RoomService, SlotService

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
        return SlotResponse.create(result), 200

    @jsoned
    def get_one(self, room_id, slot_id):
        result = self.service.get_one(slot_id) or flask.abort(404)
        return SlotResponse.create(result), 200

