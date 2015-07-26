from segue.core import db
from segue.hasher import Hasher
from segue.document.services import DocumentService

from factories import SpeakerCertificateFactory, AttendantCertificateFactory
from models import Certificate, AttendantCertificate, SpeakerCertificate, Prototype
from errors import CertificateCannotBeIssued, CertificateAlreadyIssued

class CertificateService(object):
    def __init__(self, documents=None):
        self.documents = documents or DocumentService()
        self.factories = dict(
            speaker   = SpeakerCertificateFactory(),
            attendant = AttendantCertificateFactory()
        )

    def issuable_certificates_for(self, account, exclude_issued=True):
        ticket = account.identifier_purchase
        if not ticket: return []
        if not ticket.satisfied: return []

        issued_certs = self.issued_certificates_for(account)

        if ticket.category != 'speaker':
            candidates = [ Prototype(kind='attendant', account=account, ticket=ticket) ]
        else:
            candidates = [ Prototype(kind='speaker', account=account, ticket=ticket, talk=talk) for talk in account.presented_talks ]

        if exclude_issued:
            return filter(lambda x: not self._is_like_any(x, issued_certs), candidates)
        else:
            return candidates

    def issue_certificate(self, account, kind, **payload):
        if not account: raise ValueError()

        db.session.flush()

        issued_certs   = self.issued_certificates_for(account)
        issuable_certs = self.issuable_certificates_for(account, exclude_issued=False)

        new_cert = self.factories[kind].create(account=account, **payload)

        if self._is_like_any(new_cert, issued_certs): raise CertificateAlreadyIssued()
        if not self._is_like_any(new_cert, issuable_certs): raise CertificateCannotBeIssued()

        self.documents.svg_to_pdf(new_cert.template_file, 'certificate', new_cert.hash_code, new_cert.template_vars)

        db.session.add(new_cert)
        db.session.commit()

        return new_cert

    def issued_certificates_for(self, account):
        return Certificate.query.filter(Certificate.account == account).all()

    def _is_like_any(self, candidate, issued_certs):
        return any([ issued.is_like(candidate) for issued in issued_certs ])
