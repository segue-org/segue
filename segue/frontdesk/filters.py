from segue.filters import FilterStrategies
from segue.purchase.models import Purchase
from segue.account.models import Account

class FrontDeskFilterStrategies(FilterStrategies):
    def by_customer_id(self, value, as_user=None):
        if isinstance(value, basestring) and not value.isdigit(): return
        return Purchase.id == value

    def by_customer_name(self, value, as_user=None):
        if isinstance(value, basestring) and value.isdigit(): return
        value = value.replace(" ","%")
        return Account.name.ilike('%'+value+'%')

    def by_customer_email(self, value, as_user=None):
        if isinstance(value, basestring) and "@" in value:
            return Account.email.ilike('%'+value+'%')

    def join_for_customer_name(self, queryset, needle=None):
        if isinstance(needle, basestring) and needle.isdigit():
            return queryset
        else:
            return queryset.join('customer')

    def join_for_customer_email(self, queryset, needle=None):
        if isinstance(needle, basestring) and "@" in needle:
            return queryset.join('customer')
        else:
            return queryset
