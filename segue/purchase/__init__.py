from flask.ext.jwt import current_user

from ..factory import Factory
from ..json import jsoned
from ..errors import NotAuthorized
from ..core import db, jwt_required

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

    def get_one(self, purchase_id, by=None):
        purchase = Purchase.query.get(purchase_id)
        if not self.check_ownership(purchase, by): raise NotAuthorized()
        return purchase

    def check_ownership(self, purchase, alleged):
        return purchase and alleged and purchase.customer_id == alleged.id

class PurchaseController(object):
    def __init__(self, service=None):
        self.service = service or PurchaseService()
        self.current_user = current_user

    def list(self):
        pass

    @jwt_required()
    @jsoned
    def get_one(self, purchase_id=None):
        result = self.service.get_one(purchase_id, by=self.current_user)
        return result, 200

    def pay(self):
        pass

    def notify(self):
        pass
