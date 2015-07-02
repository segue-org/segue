from models import Account
from segue.filters import FilterStrategies

POSTGRES_MAXINT = 2**31-1

class AccountFilterStrategies(FilterStrategies):
    def by_id(self, value):
        if not value.isdigit(): return

        value = int(value)
        if value > POSTGRES_MAXINT: return

        return Account.id == value

    def by_email(self, value):
        return Account.email.ilike('%'+value+'%')

    def by_name(self, value):
        return Account.name.ilike('%'+value+'%')

    def by_document(self, value):
        return Account.document.like('%'+value+'%')
