import sys
import collections

from support import *
from segue.core import db

from segue.frontdesk.services import PeopleService
from segue.purchase.services import PurchaseService
from segue.product.services import ProductService
from segue.account.services import AccountService

from segue.product.models import Product
from segue.purchase.models import Purchase

def validate_current_purchase(start=0, end=sys.maxint, fix_it=False):
    init_command()

    print "querying..."
    service = PeopleService()
    people_ids = [ p.id for p in service.by_range(int(start), int(end)) ]

    okay = 0
    wrong = 0

    for person_id in people_ids:
        person = service.get_one(person_id, check_ownership=False)
        if not person.category.startswith('proponent'):
            continue;

        print "{} scanning {}{}-{}{}...".format(F.RESET, F.GREEN, person.id, u(person.name), F.RESET),
        if person.is_valid_ticket:
            print "... {}is paid already{}".format(F.GREEN, F.RESET)
            continue

        if person.is_stale:
            print "... {}is stale{}".format(F.GREEN, F.RESET)
            continue

        if person.purchase.product in person.eligible_products:
            print "... {}product is okay{}".format(F.GREEN, F.RESET)
            okay += 1
            continue

        print "...product is {}, but eligibles are {}".format(person.purchase.product, person.eligible_products)
        wrong += 1

        if fix_it:
            new_person = service.set_product(person.id, person.eligible_products[0].id)
            print "...product has been set to {}".format(new_person.purchase.product)

    print "results: okay={}, wrong={}".format(okay, wrong)

def ensure_purchase(start=0, end=sys.maxint, commit=False):
    init_command()

    print "querying..."
    accounts = AccountService().by_range(int(start), int(end)).all()

    situations = [
        HasTicketsThatCouldBeStale(),
        HasPaidTicket(),
        IsSpeakerWithNoTicket(),
        HasPayableTicket(),
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
    print "accounts scanned: ", len(accounts)
    print "speaker purchases now:", Purchase.query.join(Product).filter(Product.category == 'speaker').count()
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
        self.purchase_svc = PurchaseService()
        self.product_svc = ProductService()
        self.count = 0
        self.solved = 0
        self.acted = 0
    def applies(self, account, known_situations):
        return False
    def inc(self):
        self.count += 1
    def solve(self, account, known_situations):
        return "was-ok"
    def __repr__(self):
        return "{}: {} cases / {} acted / {} solved".format(self.__class__.__name__, self.count, self.acted, self.solved)

class HasPaidTicket(Situation):
    def applies(self, account, known_situations):
        return account.has_valid_purchases

class HasPayableTicket(Situation):
    def applies(self, account, known_situations):
        return any([ x.payable for x in account.purchases ])

class IsSpeakerWithNoTicket(Situation):
    def applies(self, account, known_situations):
        return account.is_speaker
    def solve(self, account, known_situations):
        self.purchase_svc.give_speaker_ticket(account, commit=False)
        self.acted += 1
        self.solved += 1
        return 'solved'

class IsForeigner(Situation):
    def applies(self, account, known_situations):
        return not account.is_brazilian
    def solve(self, account, known_situations):
        self.solved += 1
        self.acted += 1
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
        buyer   = account.last_buyer
        product = self.product_svc.cheapest_for(account.guessed_category)
        print account, account.last_buyer, account.guessed_category, product
        self.purchase_svc.give_fresh_purchase(buyer, product, account, commit=False)
        self.acted += 1
        self.solved += 1
        return 'solved'
