# encoding: utf-8
import sys
from collections import defaultdict
from datetime import datetime

from segue.errors import SegueError
from segue.proposal.services import ProposalService
from segue.schedule.services import NotificationService, SlotService
from support import *;

def notify_proposals(tags=None, deadline=None, start=0, end=sys.maxint):
    init_command()
    if not tags:
        print "must specify tag names"
        sys.exit(1)
    tags = tags.split(",")
    deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
    proposals = ProposalService().all_with_tags(*tags)
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
            print "{}{}{} got raised!".format(F.RED, e.__class__.__name__, F.RESET)
            name = e.__class__.__name__
            operations[name] += 1

    print "==[ RESULTS ]========================="
    print "{}{}{} notifications got sent".format(F.GREEN, operations.pop('OK', 0), F.RESET)
    for key, value in operations.items():
        print "{}{}{} notifications resulted in {}{}{}".format(F.GREEN, value, F.RESET, F.GREEN, key, F.RESET)


def notify_slots(deadline=None, start=0, end=sys.maxint):
    init_command()
    if not deadline:
        print "must specify deadline"
        sys.exit(1)

    deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")

    slots = SlotService().query(status='dirty')
    notification = NotificationService()

    operations = defaultdict(lambda: 0)

    for slot in slots:
        if slot.id < int(start): continue;
        if slot.id > int(end): continue;

        try:
            print "{} issuing notify_slot for proposal [{}{}{}] - {}{}{} = {}{}{} @ {}{}{} (to: {}{}{})...".format(F.RESET,
                    F.GREEN, slot.talk.id, F.RESET,
                    F.GREEN, u(slot.talk.title), F.RESET,
                    F.GREEN, slot.room.name, F.RESET,
                    F.GREEN, slot.begins, F.RESET,
                    F.RED, slot.talk.owner.email, F.RESET
            ),
            notification.notify_slot(slot.id, deadline)
            print F.GREEN + "OK" + F.RESET
            operations["OK"] += 1
        except SegueError, e:
            print "{}{}{} got raised!".format(F.RED, e.__class__.__name__, F.RESET)
            name = e.__class__.__name__
            operations[name] += 1

    print "==[ RESULTS ]========================="
    print "{}{}{} notifications got sent".format(F.GREEN, operations.pop('OK', 0), F.RESET)
    for key, value in operations.items():
        print "{}{}{} notifications resulted in {}{}{}".format(F.GREEN, value, F.RESET, F.GREEN, key, F.RESET)


