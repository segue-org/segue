from segue.responses import BaseResponse

class GuideResponse(BaseResponse):
    def __init__(self, payment):
        self.payment  = payment
        self.purchase = payment.purchase
        self.buyer    = payment.purchase.buyer

class PromoCodeResponse(BaseResponse):
    def __init__(self, promocode):
        self.id          = promocode.id
        self.creator     = promocode.creator
        self.product     = promocode.product
        self.payment     = promocode.payment
        self.description = promocode.description
