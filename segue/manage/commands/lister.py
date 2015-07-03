import sys
import collections

from support import *

from segue.account.services import AccountService

def list_speakers(start=0, end=sys.maxint, commit=False):
    init_command()

    accounts = AccountService().by_range(int(start), int(end)).all()
    result = []

    for account in accounts:
        if account.is_speaker:
            print account.email
