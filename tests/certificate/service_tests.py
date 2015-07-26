import json
import mockito

from segue.errors import SegueValidationError

from segue.certificate.errors import CertificateCannotBeIssued, CertificateAlreadyIssued
from segue.certificate.services import CertificateService

from ..support.factories import *
from ..support import SegueApiTestCase, hashie, Context

class CertificateServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(CertificateServiceTestCases, self).setUp()
        self.mock_docs = mockito.Mock()
        self.service = CertificateService(documents=self.mock_docs)

    def test_account_with_no_valid_purchase_gets_zero_certs(self):
        account = self.create(ValidAccountFactory)
        purchase = self.create(ValidPurchaseFactory)

        result = self.service.issuable_certificates_for(account)
        self.assertEquals(result, [])

        result = self.service.issuable_certificates_for(purchase.customer)
        self.assertEquals(result, [])

    def test_cannot_issue_cert_for_account_with_no_valid_purchase(self):
        account = self.create(ValidAccountFactory, certificate_name='Adalberto')
        purchase = self.create(ValidPurchaseFactory)

        with self.assertRaises(CertificateCannotBeIssued):
            self.service.issue_certificate(account, 'attendant', language='pt')

        with self.assertRaises(CertificateCannotBeIssued):
            self.service.issue_certificate(purchase.customer, 'attendant', language='pt')

    def test_account_with_paid_purchase_gets_cert(self):
        account = self.create(ValidAccountFactory)
        purchase = self.create(ValidPurchaseFactory, customer=account, status='paid')

        result = self.service.issuable_certificates_for(account)

        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].kind, 'attendant')
        self.assertEquals(result[0].ticket, purchase)

    def test_issues_cert_for_account_with_paid_purchase(self):
        account = self.create(ValidAccountFactory, certificate_name='Asdrobalgilo')
        purchase = self.create(ValidPurchaseFactory, customer=account, status='paid')

        result = self.service.issue_certificate(account, 'attendant', language='pt')

        self.assertIsNotNone(result.id)
        self.assertEquals(result.kind, 'attendant')
        self.assertEquals(result.language, 'pt')
        self.assertEquals(result.name, 'Asdrobalgilo');

        mockito.verify(self.mock_docs).svg_to_pdf(result.template_file, 'certificate', result.hash_code, result.template_vars)
        self.assertEquals(result.template_file, 'certificate/templates/attendant.svg')
        self.assertEquals(result.template_vars['NOME'], 'Asdrobalgilo')
        self.assertEquals(result.template_vars['URL'],  'http://192.168.33.92/{}'.format(result.hash_code))

    def test_cannot_issue_speaker_cert_for_attendant(self):
        account = self.create(ValidAccountFactory, certificate_name='Asdrobalgilo')
        purchase = self.create(ValidPurchaseFactory, customer=account, status='paid')
        proposal = self.create(ValidProposalFactory, owner=account)

        with self.assertRaises(CertificateCannotBeIssued):
            self.service.issue_certificate(account, 'speaker', language='pt', talk=proposal)

    def setUpSpeakerScenario(self):
        account = self.create(ValidAccountFactory)
        product = self.create(ValidSpeakerProductFactory)
        purchase = self.create(ValidPurchaseFactory, customer=account, product=product, status='paid')
        prop1 = self.create(ValidProposalFactory, status='confirmed', owner=account)
        prop2 = self.create(ValidProposalFactory, status='confirmed')
        prop3 = self.create(ValidProposalFactory, status='confirmed', owner=account)
        prop4 = self.create(ValidProposalFactory, status='pending')

        self.create(ValidInviteFactory, proposal=prop2, recipient=account.email, status='accepted')
        self.create(ValidInviteFactory, proposal=prop4, recipient=account.email, status='accepted')

        slot1 = self.create(ValidSlotFactory, talk=prop1, status='confirmed')
        slot2 = self.create(ValidSlotFactory, talk=prop2, status='confirmed')
        return Context(locals())

    def test_account_of_speakers_who_presented_get_certificates(self):
        ctx = self.setUpSpeakerScenario()

        result = self.service.issuable_certificates_for(ctx.account)

        self.assertEquals(len(result), 2)

        self.assertEquals(result[0].kind, 'speaker')
        self.assertEquals(result[0].ticket, ctx.purchase)
        self.assertEquals(result[0].talk, ctx.prop1)

        self.assertEquals(result[1].kind, 'speaker')
        self.assertEquals(result[1].ticket, ctx.purchase)
        self.assertEquals(result[1].talk, ctx.prop2)

    def test_issues_certificates_to_speakers_but_only_for_presented_talks(self):
        ctx = self.setUpSpeakerScenario()

        result = self.service.issue_certificate(ctx.account, 'speaker', talk=ctx.prop1)
        self.assertIsNotNone(result.id)
        self.assertEquals(result.talk, ctx.prop1)

        result = self.service.issue_certificate(ctx.account, 'speaker', talk=ctx.prop2)
        self.assertIsNotNone(result.id)
        self.assertEquals(result.talk, ctx.prop2)

        with self.assertRaises(CertificateCannotBeIssued):
            self.service.issue_certificate(ctx.account, 'speaker', talk=ctx.prop3)

        with self.assertRaises(CertificateCannotBeIssued):
            self.service.issue_certificate(ctx.account, 'speaker', talk=ctx.prop4)

    def test_account_of_speakers_who_didnt_show_do_not_get_certificates(self):
        account = self.create(ValidAccountFactory)
        product = self.create(ValidSpeakerProductFactory)
        purchase = self.create(ValidPurchaseFactory, customer=account, product=product, status='paid')
        proposal = self.create(ValidProposalFactory, status='confirmed', owner=account)

        result = self.service.issuable_certificates_for(account)

        self.assertEquals(len(result), 0)

    def test_does_not_issue_to_noshow_speakers(self):
        account = self.create(ValidAccountFactory)
        product = self.create(ValidSpeakerProductFactory)
        purchase = self.create(ValidPurchaseFactory, customer=account, product=product, status='paid')
        proposal = self.create(ValidProposalFactory, status='confirmed', owner=account)

        with self.assertRaises(CertificateCannotBeIssued):
            self.service.issue_certificate(account, 'speaker', talk=proposal)

    def test_issued_certificates_can_be_retrieved(self):
        account = self.create(ValidAccountFactory)
        certificate = self.create(ValidCertificateFactory, account=account)

        result = self.service.issued_certificates_for(account)

        self.assertEquals(result, [ certificate ])

    def test_cannot_reissue_certificate(self):
        account = self.create(ValidAccountFactory)
        purchase = self.create(ValidPurchaseFactory, customer=account, status='paid')
        certificate = self.create(ValidAttendantCertificateFactory, account=account, ticket=purchase)

        with self.assertRaises(CertificateAlreadyIssued):
            self.service.issue_certificate(account, 'attendant')

    def test_issued_certs_are_no_longer_listed_as_issuable(self):
        account = self.create(ValidAccountFactory)
        purchase = self.create(ValidPurchaseFactory, customer=account, status='paid')
        certificate = self.create(ValidAttendantCertificateFactory, account=account, ticket=purchase)

        result = self.service.issuable_certificates_for(account)

        self.assertEquals(result, [])


