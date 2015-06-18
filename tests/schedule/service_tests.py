import mockito
from datetime import datetime, timedelta

from segue.errors import *

from ..support import SegueApiTestCase
from ..support.factories import *

from segue.schedule.services import NotificationService

class NotificationServiceTestCase(SegueApiTestCase):
    def setUp(self):
        super(NotificationServiceTestCase, self).setUp()
        self.mock_mailer = mockito.mock()
        self.mock_hasher = mockito.mock()
        self.service = NotificationService(mailer=self.mock_mailer, hasher=self.mock_hasher)

    def test_call_proposal(self):
        deadline = datetime.now() + timedelta(days=2)
        proposal = self.create_from_factory(ValidProposalWithOwnerFactory)

        mockito.when(self.mock_hasher).generate().thenReturn('ABCD')

        notification = self.service.call_proposal(proposal.id, deadline)

        self.assertEquals(notification.account, proposal.owner)
        self.assertEquals(notification.proposal.id, proposal.id)
        self.assertEquals(notification.proposal.status, 'pending')
        self.assertEquals(notification.status, 'pending')
        self.assertEquals(notification.kind, 'call')
        self.assertEquals(notification.hash, 'ABCD')

        mockito.verify(self.mock_mailer).call_proposal(notification)

    def test_retrieve_notification(self):
        existing = self.create_from_factory(ValidCallNotificationFactory, hash='DCBA')
        retrieved = self.service.get_by_hash('DCBA')
        self.assertEquals(retrieved, existing)

    def test_accept_call_proposal(self):
        today     = datetime.now().replace(hour=23,minute=59,second=59)
        yesterday = today - timedelta(days=1)
        tomorrow  = today + timedelta(days=1)

        self.create_from_factory(ValidCallNotificationFactory, hash='ABC', deadline=tomorrow)
        result = self.service.accept_notification('ABC')
        self.assertEquals(result.status, 'confirmed')
        self.assertEquals(result.proposal.status, 'confirmed')

        self.create_from_factory(ValidCallNotificationFactory, hash='DEF', deadline=yesterday)
        with self.assertRaises(NotificationExpired):
            self.service.accept_notification('DEF')

        retrieved = self.service.get_by_hash('DEF')
        self.assertEquals(retrieved.status, 'pending')
        self.assertEquals(retrieved.proposal.status, 'proposal')

    def test_decline_call_proposal(self):
        today     = datetime.now().replace(hour=23,minute=59,second=59)
        yesterday = today - timedelta(days=1)
        tomorrow  = today + timedelta(days=1)

        self.create_from_factory(ValidCallNotificationFactory, hash='ABC', deadline=tomorrow)
        result = self.service.decline_notification('ABC')
        self.assertEquals(result.status, 'declined')
        self.assertEquals(result.proposal.status, 'declined')

        self.create_from_factory(ValidCallNotificationFactory, hash='DEF', deadline=yesterday)
        with self.assertRaises(NotificationExpired):
            self.service.accept_notification('DEF')

        retrieved = self.service.get_by_hash('DEF')
        self.assertEquals(retrieved.status, 'pending')
        self.assertEquals(retrieved.proposal.status, 'proposal')


