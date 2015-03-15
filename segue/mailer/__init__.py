import yaml
import os.path
import glob

from segue.core import mailer, config
from flask_mail import Message

class TemplatedMessage(object):
    def __init__(self, template):
        self.template = template
        self.variables = { 'backend_url': config.BACKEND_URL, 'frontend_url': config.FRONTEND_URL }
        self.recipients = []

    def given(self, **args):
        self.variables.update(**args)

    def to(self, name, email):
        self.recipients.append((name, email,))

    def build(self):
        subject = self.template['subject'].format(**self.variables)
        body    = self.template['body'].format(**self.variables)

        return Message(subject, body=body, recipients=self.recipients)

class MessageFactory(object):
    def __init__(self):
        base = os.path.join(os.path.dirname(__file__), 'templates')
        pattern = os.path.join(base, '**', '*.yml')

        self._templates = {}
        for template_path in glob.glob(pattern):
            template_name = template_path.replace(base, '').replace('.yml','')[1:]
            self._templates[template_name] = yaml.load(open(template_path))

    def from_template(self, template_name):
        return TemplatedMessage(self._templates[template_name])


class MailerService(object):
    def __init__(self, templates=None, message_factory=None):
        self.message_factory = message_factory or MessageFactory()

    def proposal_invite(self, invite):
        message = self.message_factory.from_template('proposal/invite')
        message.given(invite=invite, proposal=invite.proposal, owner=invite.proposal.owner)
        message.to(invite.name, invite.recipient)

        return mailer.send(message.build())
