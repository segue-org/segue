from ..factory import Factory
from ..core import db

from segue.models import Purchase, Buyer
import schema

class BuyerFactory(Factory):
    model = Buyer

class PurchaseService(object):
    def create(self, buyer_data, product, account):
        buyer    = BuyerFactory.from_json(buyer_data, schema.buyer)
        purchase = Purchase()
        purchase.buyer = buyer
        purchase.product = product
        purchase.customer = account
        db.session.add(purchase)
        db.session.commit()
        return purchase

class PurchaseController(object):
    def list(self):
        pass

    def get_one(self):
        pass

    def pay(self):
        pass

    def notify(self):
        pass
