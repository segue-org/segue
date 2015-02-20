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
        invite = ValidInviteFactory.build()
        self.service.proposal_invite(invite)

        self.assertEquals(len(outbox), 1)
        self.assertEquals(outbox[0].recipients, [ invite.recipient ])
