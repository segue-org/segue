# encoding: utf-8

from datetime import datetime
from segue.proposal.services import ProposalService
from segue.schedule.services import NotificationService
from support import *;

def notify_proposals(deadline=None):
    init_command()
    deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
    proposals = ProposalService().all_with_tags('marked','accepted')
    notification = NotificationService()

    for proposal in proposals:
        notification.call_proposal(proposal.id, deadline)
