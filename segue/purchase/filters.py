from segue.filters import FilterStrategies

from models import Purchase, Payment

class PurchaseFilterStrategies(FilterStrategies):
    def enforce_user(self, user):
        return self.by_customer_id(user.id)

    def by_customer_id(self, value, as_user=None):
        return Purchase.customer_id == value

class PaymentFilterStrategies(FilterStrategies):
    def enforce_user(self, user):
        return self.by_customer_id(user.id)

    def by_purchase_id(self, value, as_user=None):
        return Payment.purchase_id == value

    def by_customer_id(self, value, as_user=None):
        return True




