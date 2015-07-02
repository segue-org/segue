from segue.responses import BaseResponse
from segue.schedule.responses import SlotResponse

class NonSelectionResponse(BaseResponse):
    def __init__(self, notice, links=False):
        self.id      = notice.id
        self.hash    = notice.hash

class TalkDetailResponse(BaseResponse):
    def __init__(self, talk):
        self.id    = talk.id
        self.title = talk.title
        self.track = talk.track.name_pt
        self.full  = talk.full
        self.slots     = SlotResponse.create(talk.slots.all(), embeds=False, links=False)
        self.owner     = OwnerResponse.create(talk.owner)
        self.coauthors = CoauthorResponse.create(talk.coauthors.all())

class OwnerResponse(BaseResponse):
    def __init__(self, owner):
        self.name   = owner.name
        self.resume = owner.resume

class CoauthorResponse(OwnerResponse):
    def __init__(self, coauthor):
        if coauthor.account:
            super(CoauthorResponse, self).__init__(coauthor.account)
        else:
            self.name = coauthor.name
