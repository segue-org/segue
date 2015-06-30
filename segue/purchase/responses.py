from segue.responses import BaseResponse

class GuideResponse(BaseResponse):
    def __init__(self, payment):
        self.payment  = payment
        self.purchase = payment.purchase
        self.buyer    = payment.purchase.buyer
