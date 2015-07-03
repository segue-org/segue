from segue.responses import BaseResponse

class PersonResponse(BaseResponse):
    def __init__(self, purchase, links=False):
        self.id       = person.id
        self.name     = purchase.customer.name
        self.email    = purchase.customer.email
        self.document = purchase.customer.document
        self.category = purchase.product.category
        self.price    = purchase.product.price
        self.status   = purchase.status
        self.buyer    = BuyerResponse.create(purchase.buyer)
