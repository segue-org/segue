import mockito
from datetime import datetime, timedelta

from segue.schedule.errors import *

from ..support import SegueApiTestCase, Context
from ..support.factories import *

from segue.schedule.services import NotificationService, SlotService
from segue.schedule.errors import NoSuchSlot

class SlotServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(SlotServiceTestCases, self).setUp()
        self.service = SlotService()

    def test_get_one_strictness(self):
        result = self.service.get_one(123)
        self.assertEquals(result, None)

        with self.assertRaises(NoSuchSlot):
            self.service.get_one(123, strict=True)

    def test_set_talk(self):
        talk = self.create_from_factory(ValidProposalWithOwnerFactory)
        slot = self.create_from_factory(ValidSlotFactory)

        result = self.service.set_talk(slot.id, talk.id)
        retrieved = self.service.get_one(slot.id)

        self.assertEquals(result, retrieved)
        self.assertEquals(result.talk, talk)
        self.assertEquals(result.status, 'dirty')

    def test_set_status(self):
        slot = self.create_from_factory(ValidSlotFactory)

        result = self.service.set_status(slot.id, 'confirmed')
        retrieved = self.service.get_one(slot.id)

        self.assertEquals(result, retrieved)
        self.assertEquals(result.status, 'confirmed')

    def test_empty_slot(self):
        slot = self.create_from_factory(ValidSlotFactory)
        result = self.service.empty_slot(slot.id)
        retrieved = self.service.get_one(slot.id)
        self.assertEquals(result.talk, None)
        self.assertEquals(result.status, 'empty')

    def setUpComplexScenario(self):
        day1 = datetime(2015,7,8)
        day2 = datetime(2015,7,9)
        owner1 = self.create(ValidAccountFactory, name='Arya Stark')
        owner2 = self.create(ValidAccountFactory, name='Sansa Stark')
        owner3 = self.create(ValidAccountFactory, name='Rob Baratheon')
        proposal1 = self.create(ValidProposalFactory, owner=owner1, title='Valar Morghulis')
        proposal2 = self.create(ValidProposalFactory, owner=owner2, title='Valar Dohaeris')
        proposal3 = self.create(ValidProposalFactory, owner=owner3, title='Winter is Coming')
        proposal4 = self.create(ValidProposalFactory, owner=owner3, title='You know nothing')
        room1 = self.create(ValidRoomFactory)
        room2 = self.create(ValidRoomFactory)
        slot1 = self.create(ValidSlotFactory, room=room1, talk=proposal1, begins=day1 + timedelta(hours= 9))
        slot2 = self.create(ValidSlotFactory, room=room1, talk=proposal2, begins=day1 + timedelta(hours=10))
        slot3 = self.create(ValidSlotFactory, room=room2, talk=proposal3, begins=day1 + timedelta(hours=11))
        slot3 = self.create(ValidSlotFactory, room=room1, talk=proposal4, begins=day2 + timedelta(hours= 9))

        return Context(locals())

    def test_queries_slot_by_room_and_day(self):
        ctx = self.setUpComplexScenario()

        result_with_datetime = self.service.query(room=ctx.room1.id, day=ctx.day1)

        self.assertEquals(len(result_with_datetime), 2)
        self.assertEquals(result_with_datetime[0], ctx.slot1)
        self.assertEquals(result_with_datetime[1], ctx.slot2)

        result_with_date = self.service.query(room=ctx.room1.id, day=ctx.day1.date())
        self.assertEquals(result_with_datetime, result_with_date)

    def test_query_slot_by_talk_title(self):
        ctx = self.setUpComplexScenario()
        result = self.service.query(title='Valar')

        self.assertEquals(len(result), 2)
        self.assertIn(ctx.slot1, result)
        self.assertIn(ctx.slot2, result)

    def test_needle_slot_by_talk_title(self):
        ctx = self.setUpComplexScenario()
        result = self.service.lookup('Dohaeris')
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0], ctx.slot2)

    def test_query_slot_by_speaker(self):
        ctx = self.setUpComplexScenario()
        result = self.service.query(speaker='Arya')
        self.assertEquals(len(result), 1)
        self.assertIn(ctx.slot1, result)

    def test_lookup_slot_by_speaker(self):
        ctx = self.setUpComplexScenario()
        result = self.service.lookup('Stark')
        self.assertEquals(len(result), 2)
        self.assertIn(ctx.slot1, result)
        self.assertIn(ctx.slot2, result)

    def test_annotate_slot(self):
        slot = self.create_from_factory(ValidSlotFactory)
        self.service.annotate(slot.id, 'uma anotacao')

        retrieved = self.service.get_one(slot.id)
        self.assertEquals(retrieved.annotation, 'uma anotacao')

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

    def test_notify_slot(self):
        deadline = datetime.now() + timedelta(days=2)
        proposal = self.create(ValidProposalWithOwnerFactory)
        slot = self.create(ValidSlotFactory, talk=proposal, status='dirty')

        mockito.when(self.mock_hasher).generate().thenReturn('ABCD')

        notification = self.service.notify_slot(slot.id, deadline)

        self.assertEquals(notification.account, proposal.owner)
        self.assertEquals(notification.slot.id, slot.id)
        self.assertEquals(notification.slot.status, 'pending')
        self.assertEquals(notification.status, 'pending')
        self.assertEquals(notification.kind, 'slot')
        self.assertEquals(notification.hash, 'ABCD')

        mockito.verify(self.mock_mailer).notify_slot(notification)

    def test_call_proposal_does_not_resend_if_a_similar_one_has_been_answered_already(self):
        deadline = datetime.now() + timedelta(days=2)
        proposal = self.create_from_factory(ValidProposalWithOwnerFactory)
        notification = self.create_from_factory(ValidCallNotificationFactory, proposal=proposal, status='confirmed')

        with self.assertRaises(NotificationAlreadyAnswered):
            self.service.call_proposal(proposal.id, deadline)

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
