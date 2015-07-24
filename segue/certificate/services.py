from segue.core import db
from segue.hasher import Hasher

from models import Certificate, AttendantCertificate, SpeakerCertificate

class CertificateService(object):
    def __init__(self, hasher=None):
        self.hasher = hasher or Hasher()

    def issuable_certificates_for(self, account):
        ticket = account.identifier_purchase
        if not ticket: return []
        if not ticket.satisfied: return []

        if ticket.category != 'speaker':
            return [ AttendantCertificate(account=account, ticket=ticket) ]

        return [ SpeakerCertificate(account=account, ticket=ticket, talk=talk) for talk in account.presented_talks ]
