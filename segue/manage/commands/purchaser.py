import sys
import collections

from support import *

from segue.account.services import AccountService
from segue.purchase.services import PurchaseService
from segue.proposal.services import ProposalService

def ensure_cash_purchase(start=0, end=sys.maxint):
    init_command()

    print "querying..."
    accounts = AccountService().by_range(int(start), int(end)).all()
    purchases = PurchaseService().query()
    proposals = ProposalService().query()

    print "grouping..."
    account_by_document = index(accounts,  lambda x: [ x.document ]    )
    purchase_by_account = index(purchases, lambda x: [ x.customer.id ] )
    proposal_by_email   = index(proposals, lambda x: x.related_emails  )

    report = collections.defaultdict(lambda: 0)
    solutions = collections.defaultdict(lambda: [])

    for account in accounts:
        situation = []
        print "{}scanning {}{}{} - {}{}{}...".format(F.RESET,
                F.GREEN, account.id, F.RESET,
                F.GREEN, u(account.name), F.RESET
        )

        if not account.document:
            situation.append('NoDocument')
        elif len(account_by_document[account.document]) > 1:
            situation.append('SameDocumentAsAnotherAccount')

        proposals = proposal_by_email.get(account.email, [])
        talks     = filter(lambda x: x.is_talk, proposals)

        purchases = purchase_by_account.get(account.id, [])
        tickets   = filter(lambda x: x.satisfied, purchases)
        payable   = filter(lambda x: x.payable,   purchases)

        if len(tickets) == 1:
            situation.append('OK-' + tickets[0].product.category)
            solutions['nothing-paid'].append(account)

        elif len(tickets) > 1:
            situation.append('OK-MULTI')
            solutions['nothing-paid'].append(account)

        elif talks and not purchases:
            situation.append('PENDING-SPEAKER')
            solutions['speaker'].append(account)

        elif not account.is_brazilian:
            situation.append('PENDING-FOREIGNER')
            solutions['foreigner'].append(account)

        elif len(payable) == 1:
            situation.append('PAYABLE-'+category)
            solutions['nothing-payable'].append(account)

        elif len(payable) > 1:
            situation.append('PAYABLE-MULTI'+category)
            solutions['nothing-payable'].append(account)

        elif len(purchases) == 0:
            situation.append('PURCHASES-ZERO-???')
            solutions['new-normal'].append(account)

        elif len(purchases) == 1:
            category = purchases[0].product.category
            situation.append('PURCHASES-ONE-'+category)
            solutions['new-'+category].append(account)

        elif len(purchases) > 1:
            categories = [ x.product.category for x in purchases ]
            distinct = set(categories)
            if len(distinct) == 1:
                situation.append('PURCHASES-MULTI-' + categories[0])
                solutions['new-'+categories[0]].append(account)
            else:
                situation.append('PURCHASES-MULTI-???')
                solutions['new-normal'].append(account)

        for situation in situation:
            print "--> {}{}{}".format(F.RED, situation, F.RESET)
            report[situation] += 1
        if not situation:
            report["OK"] += 1

#    db.session.commit()

    print "{} of the whole {}{}{} accounts on the system...".format(F.RESET, F.GREEN, len(accounts), F.RESET)
    for situation, count in report.items():
        print "{}we have {}{}{} accounts with {}{}{}".format(F.RESET,
                F.RED, count, F.RESET,
                F.RED, situation, F.RESET
        )

    print "{} our solutions would be...".format(F.RESET)
    for solution, cases in solutions.items():
        print "{} to execute {}{}{} on {}{}{} accounts".format(F.RESET,
                F.GREEN, solution, F.RESET,
                F.GREEN, len(cases), F.RESET
        )


def index(collection, key_fn):
    index = {}
    for element in collection:
        keys = key_fn(element)
        for key in keys:
            if key not in index: index[key] = []
            index[key].append(element)
    return index

