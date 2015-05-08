import yaml
import os.path
import glob
import codecs

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
        subject = self.template['subject'].decode('utf-8').format(**self.variables)
        body    = self.template['body'].decode('utf-8').format(**self.variables)
        bcc     = list(config.MAIL_BCC)

        return Message(subject, body=body, recipients=self.recipients, bcc=bcc)

class MessageFactory(object):
    def __init__(self):
        base = os.path.join(os.path.dirname(__file__), 'templates')
        pattern = os.path.join(base, '**', '*.yml')

        self._templates = {}
        for template_path in glob.glob(pattern):
            template_name = template_path.replace(base, '').replace('.yml','')[1:]
            self._templates[template_name] = yaml.load(codecs.open(template_path, "r", "utf-8"))

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

    def notify_payment(self, purchase, payment):
        customer = purchase.customer
        product  = purchase.product

        message = self.message_factory.from_template('purchase/confirmation')
        message.given(customer=customer, purchase=purchase, payment=payment, product=product)
        message.to(customer.name, customer.email)

        return mailer.send(message.build())

    def caravan_invite(self, invite):
        message = self.message_factory.from_template('caravan/invite')
        message.given(invite=invite, caravan=invite.caravan, owner=invite.caravan.owner)
        message.to(invite.name, invite.recipient)

        return mailer.send(message.build())

    def reset_password(self, account, reset):
        message = self.message_factory.from_template('account/reset_password')
        message.given(account=account,reset=reset)
        message.to(account.name, account.email)

        return mailer.send(message.build())

