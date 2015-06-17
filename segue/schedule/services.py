from models import Room, Slot

class RoomService(object):
    def get_one(self, room_id):
        return Room.query.get(room_id)
    def query(self, **kw):
        filters = kw
        return Room.query.filter(**filters).order_by(Room.position).all()

class SlotService(object):
    def of_room(self, room_id):
        return Slot.query.filter(Slot.room_id == room_id).all()

    def get_one(self, slot_id):
        return Slot.query.get(slot_id)
