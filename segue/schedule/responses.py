from segue.responses import BaseResponse

class RoomResponse(BaseResponse):
    def __init__(self, room, links=True):
        self.id          = room.id
        self.name        = room.name
        self.capacity    = room.capacity
        self.translation = room.translation
        self.position    = room.position
        if links:
           self.add_link('slots', room.slots, 'slots.of_room', room_id=room.id)

class SlotResponse(BaseResponse):
    def __init__(self, slot, embeds=False, links=True):
        self.id        = slot.id
        self.begins    = slot.begins
        self.hour      = slot.begins.hour
        self.duration  = slot.duration
        self.room      = slot.room.id
        self.room_name = slot.room.name
        self.blocked   = slot.blocked
        self.status    = slot.status
        if embeds:
            self.talk = TalkShortResponse.create(slot.talk)

        if links:
            self.add_link('room', slot.room, 'rooms.get_one', room_id=slot.room_id)
            self.add_link('talk', slot.talk, 'talks.get_one', talk_id=slot.talk_id)

class TalkShortResponse(BaseResponse):
    def __init__(self, talk):
        self.id    = talk.id
        self.title = talk.title
        self.owner = talk.owner.name
        self.track = talk.track.name_pt
        self.coauthors = list(set([ x.name for x in talk.coauthors ]))

class NotificationResponse(BaseResponse):
    def __init__(self, notification):
        self.id           = notification.id
        self.kind         = notification.kind
        self.hash         = notification.hash
        self.deadline     = notification.deadline
        self.status       = notification.status
        self.deadline     = notification.deadline
        self.sent         = notification.sent
        self.is_expired   = notification.is_expired

        if self.kind == 'slot':
            self.slot     = SlotResponse.create(notification.slot, links=False)
            self.proposal = notification.slot.talk
        elif self.kind == 'call':
            self.proposal = notification.proposal

