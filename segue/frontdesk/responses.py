from segue.responses import BaseResponse

class PersonResponse(BaseResponse):
    def __init__(self, person, links=False, related=True):
        self.id       = person.id
        self.name     = person.name
        self.email    = person.email
        self.document = person.document
        self.category = person.category
        self.price    = person.price
        self.status   = person.status
        self.buyer    = BuyerResponse.create(purchase.buyer)

        if related:
            self.related  = PersonResponse.create(person.related_people, related=False)
