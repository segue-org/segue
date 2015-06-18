# encoding: utf-8
import sys

from datetime import datetime
from segue.proposal.services import ProposalService
from segue.schedule.services import NotificationService
from support import *;

def notify_proposals(deadline=None, start=0, end=sys.maxint):
    init_command()
    deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
    proposals = ProposalService().all_with_tags('marked','accepted')
    notification = NotificationService()

    for proposal in proposals:
        if proposal.id < int(start): continue;
        if proposal.id > int(end): continue;

        print "{} issuing notification call_proposal for proposal {}{}{} - {}{}{} ({}{}{})...".format(F.RESET,
                F.GREEN, proposal.id, F.RESET,
                F.GREEN, u(proposal.title), F.RESET,
                F.RED, proposal.owner.email, F.RESET
        ),
        notification.call_proposal(proposal.id, deadline)
        print F.GREEN + "OK"
