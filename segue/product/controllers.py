import flask
from flask import request
from flask.ext.jwt import current_user

from segue.json import JsonFor
from segue.decorators import jsoned, jwt_only

from services import ProductService

class ProductController(object):
    def __init__(self, service=None):
        self.service = service or ProductService()
        self.current_user = current_user

    @jsoned
    def list(self):
        result = self.service.list()
        return JsonFor(result).using('ProductJsonSerializer'), 200

    @jwt_only
    @jsoned
    def purchase(self, product_id):
        data = request.get_json()
        result = self.service.purchase(data, product_id, account=self.current_user) or flask.abort(400)
        return result, 200

    @jsoned
    def caravan_products(self, hash_code):
        result = self.service.caravan_products(hash_code)
        return JsonFor(result).using('ProductJsonSerializer'), 200

    @jwt_only
    @jsoned
    def proponent_products(self):
        result = self.service.proponent_products(self.current_user) or flask.abort(404)
        return JsonFor(result).using('ProductJsonSerializer'), 200
