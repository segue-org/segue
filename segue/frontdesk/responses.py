from segue.responses import BaseResponse

class PersonResponse(BaseResponse):
    def __init__(self, person, links=False, embeds=True, related=True):
        self.id               = person.id
        self.name             = person.name
        self.email            = person.email
        self.city             = person.city
        self.document         = person.document
        self.category         = person.category
        self.price            = person.price
        self.status           = person.status
        self.related_count    = person.related_count
        self.has_valid_ticket = person.is_valid_ticket

        if embeds:
            self.buyer    = BuyerResponse.create(person.buyer)

        if related:
            self.related  = PersonResponse.create(person.related_people, embeds=False, related=False)

class BuyerResponse(BaseResponse):
    def __init__(self, buyer):
        self.id              = buyer.id
        self.kind            = buyer.kind
        self.name            = buyer.name
        self.document        = buyer.document
        self.contact         = buyer.contact
        self.address_street  = buyer.address_street
        self.address_number  = buyer.address_number
        self.address_extra   = buyer.address_extra
        self.address_zipcode = buyer.address_zipcode
        self.address_city    = buyer.address_city
        self.address_country = buyer.address_country

