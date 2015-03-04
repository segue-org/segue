from flask import request, url_for, redirect
from flask.ext.jwt import current_user
from models import Product, Purchase

from ..core import db, jwt_required
from ..factory import Factory
from ..json import jsoned, JsonFor

import schema

class PurchaseFactory(Factory):
    model = Purchase

class ProductService(object):
    def __init__(self, db_impl=None):
        self.db = db_impl or db

    def list(self):
        return Product.query.all()

    def get_product(self, id):
        return Product.query.get(id)

    def purchase(self, buyer_data, product_id, account=None):
        purchase = PurchaseFactory.from_json(buyer_data, schema.purchase)
        purchase.product = self.get_product(product_id)
        purchase.customer = account
        db.session.add(purchase)
        db.session.commit()
        return purchase


class ProductController(object):
    def __init__(self, service=None):
        self.service = service or ProductService()
        self.current_user = current_user

    @jsoned
    def schema(self, name):
        return schema.whitelist[name], 200

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
