from datetime import datetime
import mockito

from functools import wraps

from segue.core   import mailer
from segue.mailer import MailerService

from support.factories import *
from support import SegueApiTestCase

def record_messages(fn):
    @wraps(fn)
    def wrapper(instance, *args, **kw):
        with mailer.record_messages() as outbox:
            return fn(instance, outbox, *args, **kw)
    return wrapper

class MailerServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(MailerServiceTestCases, self).setUp()
        self.service = MailerService()

    @record_messages
    def test_proposal_invite(self, outbox):
        invite = self.create_from_factory(ValidInviteFactory)
        self.service.proposal_invite(invite)

        self.assertEquals(len(outbox), 1)
        self.assertEquals(len(outbox[0].recipients), 1)

        self.assertIn(invite.recipient, outbox[0].recipients[0])

        the_url = 'http://192.168.33.91:9001/api/proposals/{}/invites/{}'.format(invite.proposal.id, invite.hash)
        self.assertIn(the_url, outbox[0].body)

    @record_messages
    def test_notify_payment(self, outbox):
        product    = self.create_from_factory(ValidProductFactory, price=200)
        purchase   = self.create_from_factory(ValidPurchaseFactory, product=product, status='paid')
        payment    = self.create_from_factory(ValidPaymentFactory, type='dummy', purchase=purchase, status='paid', amount=200)

        self.service.notify_payment(purchase, payment)

        self.assertEquals(len(outbox), 1)
        self.assertEquals(len(outbox[0].recipients), 1)
        self.assertIn(purchase.customer.email, outbox[0].recipients[0])

    @record_messages
    def test_caravan_invite(self, outbox):
        invite = self.create_from_factory(ValidCaravanInviteFactory)
        self.service.caravan_invite(invite)

        self.assertEquals(len(outbox), 1)
        self.assertEquals(len(outbox[0].recipients), 1)

        self.assertIn(invite.recipient, outbox[0].recipients[0])

        the_url = 'http://192.168.33.91:9001/api/caravans/{}/invites/{}'.format(invite.caravan.id, invite.hash)
        self.assertIn(the_url, outbox[0].body)


    @record_messages
    def test_reset_password(self, outbox):
        reset = self.create_from_factory(ValidResetFactory)
        self.service.reset_password(reset.account, reset)

        self.assertEquals(len(outbox), 1)
        self.assertEquals(len(outbox[0].recipients), 1)

        self.assertIn(reset.account.email, outbox[0].recipients[0])

        the_url = 'http://192.168.33.91:9001/api/accounts/{}/reset/{}'.format(reset.account.id, reset.hash)
        self.assertIn(the_url, outbox[0].body)

    @record_messages
    def test_invite_judge(self, outbox):
        judge = self.create_from_factory(ValidJudgeFactory)
        self.service.invite_judge(judge)

        self.assertEquals(len(outbox), 1)
        self.assertEquals(len(outbox[0].recipients), 1)

        self.assertIn(judge.email, outbox[0].recipients[0])

        the_url = 'http://192.168.33.91:9001/api/judges/{}'.format(judge.hash)
        self.assertIn(the_url, outbox[0].body)

    @record_messages
    def test_call_proposal(self, outbox):
        deadline = datetime(2015,6,18,23,59,59)
        notification = self.create_from_factory(ValidCallNotificationFactory, deadline=deadline)
        self.service.call_proposal(notification)

        self.assertEquals(len(outbox), 1)
        self.assertEquals(len(outbox[0].recipients), 1)

        self.assertIn(notification.account.email, outbox[0].recipients[0])

        self.assertIn('23:59',      outbox[0].body)
        self.assertIn('18/06/2015', outbox[0].body)
        self.assertIn(notification.proposal.title, outbox[0].body)

        the_url   = 'http://192.168.33.91:9001/api/notifications/{}'.format(notification.hash)
        self.assertIn(the_url,      outbox[0].body)

    @record_messages
    def test_slot_notify(self, outbox):
        proposal = self.create(ValidProposalWithOwnerFactory)
        slot = self.create(ValidSlotFactory, begins=datetime(2015,7,8,9,0,0), talk=proposal)
        deadline = datetime(2015,6,18,23,59,59)
        notification = self.create_from_factory(ValidSlotNotificationFactory, deadline=deadline, slot=slot)

        self.service.notify_slot(notification)

        self.assertEquals(len(outbox), 1)
        self.assertEquals(len(outbox[0].recipients), 1)

        self.assertIn(notification.account.email, outbox[0].recipients[0])

        self.assertIn('09:00',    outbox[0].body)
        self.assertIn('08/07/2015', outbox[0].body)

        self.assertIn(slot.talk.title, outbox[0].body)
        self.assertIn(slot.room.name,      outbox[0].body)

        self.assertIn('23:59',      outbox[0].body)
        self.assertIn('18/06/2015', outbox[0].body)

        the_url   = 'http://192.168.33.91:9001/api/notifications/{}'.format(notification.hash)
        self.assertIn(the_url,      outbox[0].body)
