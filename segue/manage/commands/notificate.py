# encoding: utf-8
import sys
from collections import defaultdict
from datetime import datetime

from segue.proposal.services import ProposalService
from segue.schedule.services import NotificationService
from support import *;

def notify_proposals(deadline=None, start=0, end=sys.maxint):
    init_command()
    deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
    proposals = ProposalService().all_with_tags('marked','accepted')
    notification = NotificationService()

    operations = defaultdict(lambda: 0)

    for proposal in proposals:
        if proposal.id < int(start): continue;
        if proposal.id > int(end): continue;

        try:
            print "{} issuing notification call_proposal for proposal {}{}{} - {}{}{} ({}{}{})...".format(F.RESET,
                    F.GREEN, proposal.id, F.RESET,
                    F.GREEN, u(proposal.title), F.RESET,
                    F.RED, proposal.owner.email, F.RESET
            ),
            notification.call_proposal(proposal.id, deadline)
            print F.GREEN + "OK" + F.RESET
            operations["OK"] += 1
        except SegueError, e:
            name = e.__class__.__name__
            operations[name] += 1

    print "==[ RESULTS ]========================="
    print "{}{}{} notifications got sent".format(F.GREEN, operations.pop('OK'), F.RESET)
    for key, value in operations.items():
        print "{}{}{} notifications resulted in {}{}{}".format(F.GREEN, value, F.RESET, F.GREEN, key, F.RESET)


