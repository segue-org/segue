from segue.responses import BaseResponse

class CertificateResponse(BaseResponse):
    def __init__(self, certificate):
        self.id         = certificate.id
        self.kind       = certificate.kind
        self.name       = certificate.name
        self.person     = certificate.ticket.id
        self.language   = certificate.language
        self.category   = certificate.ticket.category
        self.hash_code  = certificate.hash_code
        self.issue_date = certificate.issue_date
        self.descriptor = certificate.descriptor
        self.full_url   = certificate.url
        self.status     = 'issued'

        if hasattr(certificate, 'talk'):
            self.talk = certificate.talk.title

class PrototypeResponse(BaseResponse):
    def __init__(self, prototype):
        self.kind       = prototype.kind
        self.name       = prototype.account.certificate_name
        self.person     = prototype.ticket.id
        self.category   = prototype.ticket.category
        self.descriptor = prototype.descriptor
        self.status     = 'issuable'

        if hasattr(prototype, 'talk'):
            self.talk = prototype.talk.title
