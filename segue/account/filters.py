from models import Account
from segue.filters import FilterStrategies

POSTGRES_MAXINT = 2**31-1

class AccountFilterStrategies(FilterStrategies):
    def _is_number(self, value):
        if not value.isdigit(): return False
        value = int(value)
        if value > POSTGRES_MAXINT: return False
        return True

    def by_email(self, value):
        if self._is_number(value): return
        return Account.email.ilike('%'+value+'%')

    def by_name(self, value):
        if self._is_number(value): return
        return Account.name.ilike('%'+value+'%')

    def by_document(self, value):
        if len(value) > 4:
            return Account.document.like('%'+value+'%')

    def by_purchase_id(self, value, as_user=None):
        from segue.purchase.models import Purchase
        if not self._is_number(value): return

        return Purchase.id == value

    def join_for_purchase_id(self, queryset):
        from segue.purchase.models import Purchase
        return queryset.join(Purchase)

