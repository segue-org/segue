from models import Account
from segue.filters import FilterStrategies

def _looks_like_an_id(value):
    return isinstance(value, basestring) and value.isdigit() and int(value) < 10**5

class AccountFilterStrategies(FilterStrategies):
    def by_purchase_id(self, value):
        if not _looks_like_an_id(value): return
        from segue.purchase.models import Purchase
        return Purchase.id == value

    def by_id(self, value):
        if not _looks_like_an_id(value): return
        return Account.id == value

    def by_email(self, value):
        return Account.email.ilike('%'+value+'%')

    def by_name(self, value):
        return Account.name.ilike('%'+value+'%')

    def by_document(self, value):
        if _looks_like_an_id(value): return
        return Account.document.like('%'+value+'%')

    def join_for_purchase_id(self, queryset, needle=None):
        if _looks_like_an_id(needle):
            return queryset.join('purchases')
        else:
            return queryset
