from segue.responses import BaseResponse

class PersonResponse(BaseResponse):
    def __init__(self, person, links=True):
        self.id               = person.id
        self.name             = person.name
        self.email            = person.email
        self.city             = person.city
        self.country          = person.country
        self.document         = person.document
        self.category         = person.category
        self.price            = person.price
        self.status           = person.status
        self.related_count    = person.related_count
        self.has_valid_ticket = person.is_valid_ticket

        if links:
            self.add_link('related',  person.related_count, 'fd.person.related',  person_id=person.id)
            self.add_link('buyer',    person.buyer,         'fd.person.buyer',    person_id=person.id)
            self.add_link('eligible', None,                 'fd.person.eligible', person_id=person.id)

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


class ProductResponse(BaseResponse):
    def __init__(self, product):
        self.id                = product.id
        self.kind              = product.kind
        self.category          = product.category
        self.public            = product.public
        self.price             = product.price
        self.sold_until        = product.sold_until
        self.description       = product.description
        self.is_promo          = product.is_promo
        self.is_speaker        = product.is_speaker
        self.gives_kit         = product.gives_kit
        self.can_pay_cash      = product.can_pay_cash
        self.original_deadline = product.original_deadline
