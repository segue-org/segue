from segue.filters import FilterStrategies
from models import PromoCode
from segue.account.models import Account

class PromoCodeFilterStrategies(FilterStrategies):
    def by_creator_name(self, value, as_user=None):
        return Account.name.ilike('%'+value+'%')

    def by_hash_code(self, value, as_user=None):
        return PromoCode.hash_code.ilike("%"+value+"%")

    def by_used(self, value, as_user=None):
        if not isinstance(value, bool): return None
        if value:
            return PromoCode.payment != None
        return PromoCode.payment == None

    def by_description(self, value, as_user=None):
        return PromoCode.description.ilike("%"+value+"%")

    def join_for_creator_name(self, queryset):
        return queryset.join(Account)

