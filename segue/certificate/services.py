from segue.core import db
from segue.hasher import Hasher

from factories import SpeakerCertificateFactory, AttendantCertificateFactory
from models import Certificate, AttendantCertificate, SpeakerCertificate
from errors import CertificateCannotBeIssued

class CertificateService(object):
    def __init__(self, hasher=None):
        self.hasher = hasher or Hasher()
        self.factories = dict(
            speaker   = SpeakerCertificateFactory(),
            attendant = AttendantCertificateFactory()
        )

    def issuable_certificates_for(self, account):
        ticket = account.identifier_purchase
        if not ticket: return []
        if not ticket.satisfied: return []

        if ticket.category != 'speaker':
            return [ AttendantCertificate(account=account, ticket=ticket) ]

        return [ SpeakerCertificate(account=account, ticket=ticket, talk=talk) for talk in account.presented_talks ]

    def issue_certificate(self, account, kind, **payload):
        if not account: raise ValueError()

        issuable_certs = self.issuable_certificates_for(account)

        new_cert = self.factories[kind].create(account=account, **payload)

        is_valid = any([ new_cert.is_like(possible) for possible in issuable_certs ])
        if not is_valid: raise CertificateCannotBeIssued()

        db.session.add(new_cert)
        db.session.commit()

        return new_cert
