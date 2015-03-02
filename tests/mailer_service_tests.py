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

