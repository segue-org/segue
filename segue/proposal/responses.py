from segue.responses import BaseResponse

class NonSelectionResponse(BaseResponse):
    def __init__(self, notice, links=False):
        self.id      = notice.id
        self.hash    = notice.hash
