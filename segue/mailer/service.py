import yaml
import os.path

from segue.core import mailer, config
from flask_mail import Message

class Template(dict):
    def __init__(self, **template_data):
        self.template_data = template_data
        self.recipients = [];

    def given(self, **kw):
        self.update(**kw)

    def to(self, *recipients):
        self.recipients.append(recipients)

    def build(self):
        subject = self.template_data['subject'].format(**self)
        body    = self.template_data['body'].format(**self)

        return Message(subject, body=body, recipients=self.recipients)

class TemplateLoader(dict):
    def __init__(self):
        base = os.path.dirname(__file__)
        templates = ['proposal/invite']
        for template in templates:
            path = os.path.join(base, 'templates', template + '.yml')
            self[template] = Template(**yaml.load(open(path)))

class MailerService(object):
    def __init__(self, templates=None):
        self.templates = templates or TemplateLoader()

    def proposal_invite(self, invite):
        template = self.templates['proposal/invite']
        template.given(invite=invite, proposal=invite.proposal, owner=invite.proposal.owner)
        template.to((invite.name, invite.recipient,))

        return mailer.send(template.build())
