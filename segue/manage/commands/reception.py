import sys
import collections

from support import *

from segue.frontdesk.services import BadgeService, PeopleService

USAGE = """
    python manage.py reception_mail --categories=comma_separated_categories --status=paid|pending --start=id, --end=id

"""

def reception_mail(status, categories="", start=None, end=None):
    if not start:      print USAGE; return;
    if not end:        print USAGE; return;
    if not categories: print USAGE; return;
    if not status:     print USAGE; return;

    init_command()

    wanted_categories = categories.split(",")
    people = PeopleService()
    errors = []

    for person in people.by_range(int(start), int(end)):
        print "scanning {}{}{}, person {}{}{} - {}{}{} - {}{}{}".format(F.RESET,
            F.RED, person.id,       F.RESET,
            F.RED, u(person.name),  F.RESET,
            F.RED, person.status,   F.RESET,
            F.RED, person.category, F.RESET
        )
        print "... email is {}{}{}".format(F.RED, person.email.__repr__(), F.RESET)

        if person.status != status:
            print "... {}ticket does not have the correct status{}, skipping".format(F.RED, F.RESET)
            continue

        elif person.category in wanted_categories or categories == "*":
            print "... {}category is correct{}, sending".format(F.GREEN, F.RESET)
            try:
                people.send_reception_mail(person.id)
            except Exception, e:
                errors.append([ person.id, sys.exc_info() ])

        else:
            print "... {}wrong category{}, skipping".format(F.RED, F.RESET)

    for id, error in errors:
        print "ERROR for person {}: {}".format(person.id, error)


