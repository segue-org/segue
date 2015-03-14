from flask import request, url_for, redirect
from flask.ext.jwt import current_user

from ..core import db, jwt_required
from ..factory import Factory
from ..json import jsoned, JsonFor

from models import Product
from segue.purchase.services import PurchaseService

class ProductService(object):
    def __init__(self, db_impl=None, purchases=None):
        self.db        = db_impl or db
        self.purchases = purchases or PurchaseService();

    def list(self):
        return Product.query.all()

    def get_product(self, id):
        return Product.query.get(id)

    def purchase(self, buyer_data, product_id, account=None):
        product = self.get_product(product_id)
        return self.purchases.create(buyer_data, product, account)

class ProductController(object):
    def __init__(self, service=None):
        self.service = service or ProductService()
        self.current_user = current_user

    @jsoned
    def list(self):
        result = self.service.list()
        return JsonFor(result).using('ProductJsonSerializer'), 200

    @jwt_required()
    @jsoned
    def purchase(self, product_id):
        data = request.get_json()
        result = self.service.purchase(data, product_id, account=self.current_user) or flask.abort(400)
        return result, 200
