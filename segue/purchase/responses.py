from segue.responses import BaseResponse
from segue.purchase.promocode.models import PromoCodePayment

class GuideResponse(BaseResponse):
    def __init__(self, payment):
        self.payment   = payment
        self.purchase  = payment.purchase
        self.buyer     = payment.purchase.buyer
        if isinstance(payment, PromoCodePayment):
            self.promocode = PromoCodeResponse.create(payment.promocode)
        payments       = payment.purchase.valid_payments
        for p in payments:
            if isinstance(p, PromoCodePayment):
                self.promocode = PromoCodeResponse.create(p.promocode)
                break

class PromoCodeResponse(BaseResponse):
    def __init__(self, promocode):
        self.id          = promocode.id
        self.creator     = promocode.creator
        self.product     = promocode.product
        self.payment     = promocode.payment
        self.discount    = promocode.discount
        self.description = promocode.description
        self.hash_code   = promocode.hash_code
