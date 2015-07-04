import sys
import collections

from support import *

from segue.frontdesk.services import BadgeService, PeopleService

USAGE = """
    python manage.py print_categories --categories=comma_separated_categories --start=id, --end=id --printer=PRINTER

"""

def print_categories(categories="", start=None, end=None, printer=None):
    if not start:      print USAGE; return;
    if not end:        print USAGE; return;
    if not categories: print USAGE; return;
    if not printer:    print USAGE; return;
    init_command()

    wanted_categories = categories.split(",")
    people = PeopleService()
    badges = BadgeService()
    result = []

    for person in people.by_range(int(start), int(end)):
        print "scanning {}{}{}, person {}{}{} - {}{}{}".format(F.RESET,
            F.RED, person.id,       F.RESET,
            F.RED, u(person.name),  F.RESET,
            F.RED, person.category, F.RESET
        )

        if person.category not in wanted_categories:
            print "... {}wrong category{}, skipping".format(F.RED, F.RESET)
            continue

        if not person.is_valid_ticket:
            print "... {}ticket is not valid{}, skipping".format(F.RED, F.RESET)
            continue

        print "... {}correct category{}, printing".format(F.GREEN, F.RESET)

        badges.make_badge_for_person(printer, person)

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
    badges.make_badge_for_person(printer, person)