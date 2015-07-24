import json
import mockito

from segue.errors import SegueValidationError
from segue.certificate.services import CertificateService

from ..support.factories import *
from ..support import SegueApiTestCase, hashie, Context

class CertificateServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(CertificateServiceTestCases, self).setUp()
        self.mock_hasher = mockito.Mock()
        self.service = CertificateService(hasher=self.mock_hasher)


    def test_account_with_no_valid_purchase_gets_zero_certs(self):
        account = self.create(ValidAccountFactory)
        purchase = self.create(ValidPurchaseFactory)

        result = self.service.issuable_certificates_for(account)
        self.assertEquals(result, [])

        result = self.service.issuable_certificates_for(purchase.customer)
        self.assertEquals(result, [])


    def test_account_with_paid_purchase_gets_cert(self):
        account = self.create(ValidAccountFactory)
        purchase = self.create(ValidPurchaseFactory, customer=account, status='paid')

        result = self.service.issuable_certificates_for(account)

        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].kind, 'attendant')
        self.assertEquals(result[0].ticket, purchase)
        self.assertEquals(result[0].id, None)

    def test_account_of_speakers_who_presented_get_certificates(self):
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

        result = self.service.issuable_certificates_for(account)

        self.assertEquals(len(result), 2)

        self.assertEquals(result[0].kind, 'speaker')
        self.assertEquals(result[0].ticket, purchase)
        self.assertEquals(result[0].talk, prop1)
        self.assertEquals(result[0].id, None)

        self.assertEquals(result[1].kind, 'speaker')
        self.assertEquals(result[1].ticket, purchase)
        self.assertEquals(result[1].talk, prop2)
        self.assertEquals(result[1].id, None)

    def test_account_of_speakers_who_didnt_show_do_not_get_certificates(self):
        account = self.create(ValidAccountFactory)
        product = self.create(ValidSpeakerProductFactory)
        purchase = self.create(ValidPurchaseFactory, customer=account, product=product, status='paid')
        proposal = self.create(ValidProposalFactory, status='confirmed', owner=account)

        result = self.service.issuable_certificates_for(account)

        self.assertEquals(len(result), 0)
