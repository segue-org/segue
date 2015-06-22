from flask import request, abort
from flask.ext.jwt import current_user

from segue.core import cache
from segue.decorators import jsoned, jwt_only, admin_only

from segue.schedule.services import RoomService, SlotService

from ..responses import *

class AdminScheduleController(object):
    def __init__(self, rooms=None, slots=None):
        self.current_user = current_user
        self.rooms = rooms or RoomService()
        self.slots = slots or SlotService()

    @jwt_only
    @admin_only
    @jsoned
    def list_rooms(self):
        result = self.rooms.query()
        return RoomResponse.create(result), 200

    @jwt_only
    @admin_only
    @jsoned
    def query_slots(self):
        criteria = request.args.to_dict()
        result = self.slots.query(**criteria)
        return SlotResponse.create(result, links=False), 200

    @jwt_only
    @admin_only
    @jsoned
    def get_slot(self, slot_id):
        result = self.slots.get_one(slot_id) or abort(404)
        return SlotResponse.create(result, links=False), 200

    @jwt_only
    @admin_only
    @jsoned
    def block_slot(self, slot_id):
        result = self.slots.set_blocked(slot_id,True) or abort(404)
        return SlotResponse.create(result, links=False), 200

    @jwt_only
    @admin_only
    @jsoned
    def unblock_slot(self, slot_id):
        result = self.slots.set_blocked(slot_id,False) or abort(404)
        return SlotResponse.create(result, links=False), 200
