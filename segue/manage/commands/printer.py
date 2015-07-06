import sys
import collections

from support import *

from segue.frontdesk.services import BadgeService, PeopleService

USAGE = """
    python manage.py print_categories --categories=comma_separated_categories
                                      --start=id,
                                      --end=id
                                      --printer=PRINTER
                                      --rehearse
                                      [--failures_only|--never_printed_only]

"""

def mark_failed(ids=''):
    init_command()

    service = BadgeService()
    for person_id in map(int, ids.split(",")):
        print "marking last badge attempt for person {}{}{} as failed...".format(F.RED, person_id, F.RESET),
        result = service.mark_failed_for_person(person_id)
        print result

def print_range(categories="", start=None, end=None, printer=None, failures_only=False, never_printed_only=False, rehearse=False):
    if not start:      print USAGE; return;
    if not end:        print USAGE; return;
    if not categories: print USAGE; return;
    if not printer:    print USAGE; return;
    if failures_only and never_printed_only: print USAGE; return;
    init_command()

    wanted_categories = categories.split(",")
    people = PeopleService()
    badges = BadgeService()

    printed = 0

    for person in people.by_range(int(start), int(end)):
        print "{}scanning id {}{}{}, name {}{}{}, category {}{}{}".format(F.RESET,
            F.RED, person.id,       F.RESET,
            F.RED, u(person.name),  F.RESET,
            F.RED, person.category, F.RESET
        )

        if person.category in wanted_categories:
            print "... {}has correct category{}".format(F.GREEN, F.RESET)
        elif categories == "*":
            print "... {}has correct category{}".format(F.GREEN, F.RESET)
        else:
            print "... {}wrong category{}, skipping".format(F.RED, F.RESET)
            continue

        if not person.is_valid_ticket:
            print "... {}ticket is not valid{}, skipping".format(F.RED, F.RESET)
            continue
        print "... {}has valid ticket{}".format(F.GREEN, F.RESET)

        was_printed_before  = badges.was_ever_printed(person.id)
        has_failed_recently = badges.has_failed_recently(person.id)

        if never_printed_only and was_printed_before:
            print "... {}was printed before{}, skipping".format(F.RED, F.RESET)
            continue
        elif failures_only and not has_failed_recently:
            print "... {}did not fail recently{}, skipping".format(F.RED, F.RESET)
            continue
        elif rehearse:
            print "... {}matches printing criteria{}, so I would print it".format(F.GREEN, F.RESET)
            printed += 1
            continue

        print "... {}matches printing criteria{}, printing".format(F.GREEN, F.RESET)
        printed += 1
        badges.make_badge(printer, person.id)

    if rehearse:
        print "WOULD BE PRINTED", printed
    else:
        print "TOTAL PRINTED:", printed

def print_person(xid):
    init_command()

    person = PeopleService().get_one(int(xid))
    badges = BadgeService()
    result = []

    print "scanning {}{}{}, person {}{}{} - {}{}{}".format(F.RESET,
        F.RED, person.id,       F.RESET,
        F.RED, u(person.name),  F.RESET,
        F.RED, person.category, F.RESET
        )

    if not person.is_valid_ticket:
        print "... {}ticket is not valid{}, skipping".format(F.RED, F.RESET)
        return

    print "... printing"
    badges.make_badge(printer, person)
