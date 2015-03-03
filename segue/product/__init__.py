from flask import request, url_for, redirect
from models import Product

from ..core import db, jwt_required
from ..factory import Factory
from ..json import jsoned, JsonFor

import schema

class ProductService(object):
    def __init__(self, db_impl=None):
        self.db = db_impl or db

    def list(self):
        return Product.query.all()

class ProductController(object):
    def __init__(self, service=None):
        self.service = service or ProductService()

    @jsoned
    def list(self):
        result = self.service.list()
        return JsonFor(result).using('ProductJsonSerializer'), 200

    def purchase(self):
        pass
