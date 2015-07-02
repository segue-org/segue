import sys
import collections

from support import *
from segue.core import db

from segue.purchase.models import Purchase
from segue.account.services import AccountService

def ensure_purchase(start=0, end=sys.maxint, commit=False):
    init_command()

    print "querying..."
    accounts = AccountService().by_range(int(start), int(end)).all()

    report = collections.defaultdict(lambda: 0)
    solutions = collections.defaultdict(lambda: [])

    situations = [
        HasTicketsThatCouldBeStale(),
        HasPaidTicket(),
        HasPayableTicket(),
        IsSpeaker(),
        IsForeigner(),
        HasZeroPayableTickets(),
    ]

    not_solved = collections.defaultdict(list)

    for account in accounts:
        known_situations = []
        print "\n{} running {}{}-{}{}...".format(F.RESET, F.GREEN, account.id, u(account.name), F.RESET),

        for situation in situations:

            print "{}{}{}?...".format(F.BLUE, situation.__class__.__name__, F.RESET),

            if situation.applies(account, known_situations):
                situation.inc()
                known_situations.append(situation)
                print "{}YES{}".format(F.RED, F.RESET),

                solution_status = situation.solve(account, known_situations)

                if solution_status == 'solved':
                    print "{}SOLVED!{}".format(F.GREEN, F.RESET),
                    break
                elif solution_status == 'was-ok':
                    print "{}WAS OK{}".format(F.GREEN, F.RESET),
                    break
                elif solution_status == 'continue':
                    print "/",
                    continue
                else:
                    print "{}NOT SOLVED!{}".format(F.REF, F.RESET),
                    not_solved[situation.__class__.__name__].push(account)

    print "\n*************"
    print "stale purchases now:", Purchase.query.filter(Purchase.status == 'stale').count()
    print not_solved
    for situation in situations:
        print situation
    if commit:
        print "committing!"
        db.session.commit()
    else:
        print "rolling back!"
        db.session.rollback()
    print "OK"

class Situation(object):
    def __init__(self):
        self.count = 0
        self.solved = 0
        self.acted = 0
    def applies(self, account, known_situations):
        return False
    def solve(self, account, known_situations):
        return "was-ok"
    def inc(self):
        self.count += 1
    def __repr__(self):
        return "{}: {} cases / {} acted / {} solved".format(self.__class__.__name__, self.count, self.acted, self.solved)

class HasPaidTicket(Situation):
    def applies(self, account, known_situations):
        return account.has_valid_purchases

class HasPayableTicket(Situation):
    def applies(self, account, known_situations):
        return any([ x.payable for x in account.purchases ])

class IsSpeaker(Situation):
    def applies(self, account, known_situations):
        return account.is_speaker
    def solve(self, account, known_situations):
        self.acted += 1
        self.solved += 1
        return 'solved'

class IsForeigner(Situation):
    def applies(self, account, known_situations):
        return not account.is_brazilian
    def solve(self, account, known_situations):
        self.acted += 1
        self.solved += 1
        return 'solved'

class HasTicketsThatCouldBeStale(Situation):
    def applies(self, account, known_situations):
        stale_tickets = filter(lambda x: x.could_be_stale, account.purchases)
        return len(stale_tickets) > 0
    def solve(self, account, known_situations):
        stale_tickets = filter(lambda x: x.could_be_stale, account.purchases)
        print "stalifying {}...".format(len(stale_tickets)),
        for purchase in stale_tickets:
            purchase.status = 'stale'
            db.session.add(purchase)
        self.acted += 1
        return 'continue'

class HasZeroPayableTickets(Situation):
    def applies(self, account, known_situations):
        return all([ x.stale for x in account.purchases])
    def solve(self, account, known_situations):
        self.acted += 1
        self.solved += 1
        return 'solved'
