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
        subject = unicode(self.template['subject']).format(**self.variables)
        body    = unicode(self.template['body']).format(**self.variables)
        bcc     = list(config.MAIL_BCC)

        return Message(subject, body=body, recipients=self.recipients, bcc=bcc)

class MessageFactory(object):
    def __init__(self):
        base = os.path.join(os.path.dirname(__file__), 'templates')
        pattern = os.path.join(base, '**', '*.yml')

        self._templates = {}
        for template_path in glob.glob(pattern):
            template_name = template_path.replace(base, '').replace('.yml','')[1:]
            self._templates[template_name] = yaml.load(codecs.open(template_path))

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

    def invite_judge(self, token):
        message = self.message_factory.from_template('judge/invite')
        message.given(token=token)
        message.to('', token.email)

        return mailer.send(message.build())

    def call_proposal(self, notification):
        message = self.message_factory.from_template('schedule/call_proposal')
        message.given(
            notification   = notification,
            account        = notification.account,
            proposal       = notification.proposal,
            deadline_hours = notification.deadline.strftime("%H:%M"),
            deadline_day   = notification.deadline.strftime("%d/%m/%Y")
        )
        message.to(notification.account.name, notification.account.email)
        return mailer.send(message.build())

    def notify_slot(self, notification):
        message = self.message_factory.from_template('schedule/notify_slot')
        message.given(
            room               = notification.slot.room,
            account            = notification.account,
            proposal           = notification.slot.talk,
            notification       = notification,
            deadline_day       = notification.deadline.strftime("%d/%m/%Y"),
            deadline_hours     = notification.deadline.strftime("%H:%M"),
            presentation_day   = notification.slot.begins.strftime("%d/%m/%Y"),
            presentation_hours = notification.slot.begins.strftime("%H:%M")
        )
        message.to(notification.account.name, notification.account.email)
        return mailer.send(message.build())
