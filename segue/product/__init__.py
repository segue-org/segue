from flask import request, url_for, redirect
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

    def purchase(self, buyer_data, account=None):
        pass


class ProductController(object):
    def __init__(self, service=None):
        self.service = service or ProductService()

    @jsoned
    def schema(self, name):
        return schema.whitelist[name], 200

    @jsoned
    def list(self):
        result = self.service.list()
        return JsonFor(result).using('ProductJsonSerializer'), 200

    @jwt_required()
    @jsoned
    def purchase(self):
        data = request.get_json()
        result = self.service.purchase(data, account=self.current_user) or flask.abort(400)
        return result, 200
