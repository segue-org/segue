from segue.core import db
from segue.models import Account, Proposal, ProposalInvite
from tests.support.factories import *

def populate(clean=False):
    if clean:
        ProposalInvite.query.delete()
        Proposal.query.delete()
        Account.query.delete()
    accounts = [
        ValidAccountFactory.build(password='1234'),
        ValidAccountFactory.build(password='1234'),
        ValidAccountFactory.build(password='1234'),
    ]
    proposals = [
        ValidProposalFactory.build(owner=accounts[0]),
        ValidProposalFactory.build(owner=accounts[0]),
        ValidProposalFactory.build(owner=accounts[1]),
        ValidProposalFactory.build(owner=accounts[1]),
    ]
    proposal_invites = [
        ValidInviteFactory.build(proposal=proposals[0]),
        ValidInviteFactory.build(proposal=proposals[0]),
        ValidInviteFactory.build(proposal=proposals[0]),
    ]
    db.session.add_all(accounts)
    db.session.add_all(proposals)
    db.session.add_all(proposal_invites)
    db.session.commit()
