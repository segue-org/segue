import mockito

from functools import wraps

from segue.core   import mailer
from segue.mailer import MailerService, Template

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
        self.mock_templates = dict(a=1)
        self.service = MailerService(templates=self.mock_templates)

    def _fake_template(self, path, subject, body):
        self.mock_templates[path] = Template(subject=subject, body=body)

    @record_messages
    def test_proposal_invite(self, outbox):
        self._fake_template('proposal/invite', 'ueon', 'cachero')

        invite = ValidInviteFactory.build()
        self.service.proposal_invite(invite)

        self.assertEquals(len(outbox), 1)
        self.assertEquals(len(outbox[0].recipients), 1)
        self.assertIn(invite.recipient, outbox[0].recipients[0])
        self.assertEquals(outbox[0].body, 'cachero')
        self.assertEquals(outbox[0].subject, 'ueon')

