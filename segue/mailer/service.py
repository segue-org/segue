from segue.core import mailer
from flask_mail import Message

class MailerService(object):
    def proposal_invite(self, invite):
        recipients = [ invite.recipient ]
        subject = "convite de co-autor de proposta de palestra"
        body    = "{proposal.owner.name} te convidou para ser co-autor da palestra {proposal.title}".format(proposal=invite.proposal)
        msg = Message(subject, body=body, recipients=recipients)
        return mailer.send(msg)
