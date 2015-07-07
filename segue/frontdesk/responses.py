from segue.responses import BaseResponse

class PersonResponse(BaseResponse):
    def __init__(self, person, embeds=False, links=True):
        self.id                 = person.id
        self.name               = person.name
        self.email              = person.email
        self.city               = person.city
        self.country            = person.country
        self.document           = person.document
        self.category           = person.category
        self.price              = person.price
        self.status             = person.status
        self.kind               = person.kind
        self.badge_name         = person.badge_name
        self.badge_corp         = person.badge_corp
        self.is_brazilian       = person.is_brazilian
        self.reception_desk     = person.reception_desk

        self.related_count         = person.related_count
        self.has_valid_ticket      = person.is_valid_ticket
        self.can_change_product    = person.can_change_product
        self.outstanding_amount    = person.outstanding_amount
        self.can_change_badge_corp = person.can_change_badge_corp

        if embeds:
            self.payments   = PaymentResponse.create(person.purchase.valid_payments.all())
            self.product    = ProductResponse.create(person.purchase.product)
            self.last_badge = BadgeResponse.create(person.last_badge)

        if links:
            self.add_link('related',  person.related_count,     'fd.person.related',  person_id=person.id)
            self.add_link('buyer',    person.buyer,             'fd.person.buyer',    person_id=person.id)
            self.add_link('eligible', -1,                       'fd.person.eligible', person_id=person.id)

class BadgeResponse(BaseResponse):
    def __init__(self, badge):
        self.id      = badge.id
        self.prefix  = badge.prefix
        self.name    = badge.name
        self.corp    = badge.organization
        self.printer = badge.printer
        self.was_ok  = badge.was_ok
        self.given   = badge.given

class VisitorResponse(BaseResponse):
    def __init__(self, visitor):
        self.id     = visitor.id
        self.name   = visitor.name
        self.email  = visitor.email

class ReceptionResponse(PersonResponse):
    def __init__(self, person):
        super(ReceptionResponse, self).__init__(person, embeds=True, links=False)
        self.buyer = BuyerResponse.create(person.buyer)

class PaymentResponse(BaseResponse):
    def __init__(self, payment):
        self.id     = payment.id
        self.type   = payment.type
        self.amount = payment.amount
        self.status = payment.status
        setattr(self, payment.type, payment.extra_fields)

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
