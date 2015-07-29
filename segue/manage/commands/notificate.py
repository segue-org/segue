# encoding: utf-8
import sys
from collections import defaultdict
from datetime import datetime

from segue.errors import SegueError
from segue.account.services import AccountService
from segue.proposal.services import ProposalService, NonSelectionService
from segue.schedule.services import NotificationService, SlotService
from segue.certificate.services import CertificateService
from segue.mailer import MailerService
from support import *;

def certificates(start=0, end=sys.maxint):
    init_command()

    accounts     = AccountService().by_range(int(start), int(end)).all()
    certificates = CertificateService()
    mailer       = MailerService()

    skipped = 0
    sent    = 0

    for account in accounts:
        print "{}{}{} - account owned by {}{}{}...".format(
                F.RED, account.id, F.RESET,
                F.RED, account.email, F.RESET
        ),

        available_certs = certificates.issuable_certificates_for(account, exclude_issued=True)

        if not available_certs:
            print "has {}0{} pending certs, {}skipping{}".format(F.RED, F.RESET, F.RED, F.RESET)
            skipped += 1
            continue

        if not account.email:
            print "{}this account has no email{}, skipping".format(F.RED, F.RESET)
            continue

        print "has certs = {}{}{}, {}notifying{}".format(F.RED, available_certs, F.RESET, F.GREEN, F.RESET)
        mailer.certificates_available(account, available_certs)
        sent += 1

    print "============== RESULTS ==============="
    print "start: {}{}{}, end: {}{}{}".format(F.GREEN, start, F.RESET, F.GREEN, end, F.RESET)
    print "accounts scanned: {}{}{}".format(F.GREEN, len(accounts), F.RESET)
    print "         skipped: {}{}{}".format(F.GREEN, skipped,       F.RESET)
    print "      sent email: {}{}{}".format(F.GREEN, sent,          F.RESET)

def non_selection(start=0, end=sys.maxint):
    init_command()

    accounts = AccountService().by_range(int(start), int(end)).all()
    service = NonSelectionService()

    results = { True: 0, False: 0 }

    for account in accounts:
        print "{}{}{} - account owned by {}{}{}...".format(
                F.RED, account.id, F.RESET,
                F.RED, account.email, F.RESET
        ),

        qualifies, earliest_proposal = service.qualify(account)
        results[qualifies] += 1

        message = F.GREEN+'qualifies...' if qualifies else F.RED+'does not qualify!'
        print message+F.RESET,

        if qualifies:
            print "{}sending{}...".format(F.GREEN, F.RESET),
            service.create_and_send(account)

        print F.GREEN+"OK"+F.RESET

    print "============== RESULTS ==============="
    print "start: {}{}{}, end: {}{}{}".format(F.GREEN, start, F.RESET, F.GREEN, end, F.RESET)
    print "accounts scanned: {}{}{}".format(F.GREEN, len(accounts),  F.RESET)
    print "       qualified: {}{}{}".format(F.GREEN, results[True],  F.RESET)
    print "   not qualified: {}{}{}".format(F.GREEN, results[False], F.RESET)

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

    all_slots = SlotService().query(status='dirty')
    all_slots.sort(key=lambda x: x.id)
    notification = NotificationService()

    operations = defaultdict(lambda: 0)

    for slot in all_slots:
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


