import flask
from flask import request, url_for
from flask.ext.jwt import current_user

from datetime import datetime
from ..core import db, jwt_required
from ..json import jsoned, JsonFor

from models import Product
from segue.errors import ProductExpired, InvalidCaravan
from segue.purchase.services import PurchaseService
from segue.caravan.services import CaravanService
from segue.caravan.models import CaravanProduct

DEFAULT_ORDERING = Product.sold_until

class ProductService(object):
    def __init__(self, db_impl=None, purchases=None, caravans=None):
        self.db         = db_impl or db
        self.purchases  = purchases or PurchaseService()
        self.caravans   = caravans or CaravanService()

    def _in_time(self):
        return Product.sold_until >= datetime.now()

    def _is_public(self):
        return Product.public == True

    def list(self):
        return Product.query.filter(self._in_time(), self._is_public()).order_by(DEFAULT_ORDERING).all()

    def caravan_products(self, hash_code):
        return CaravanProduct.query.filter(self._in_time()).order_by(DEFAULT_ORDERING).all()

    def get_product(self, product_id):
        return Product.query.get(product_id)

    def purchase(self, buyer_data, product_id, account=None):
        product = self.get_product(product_id)
        product.check_eligibility(buyer_data)
        extra_fields = product.extra_purchase_fields_for(buyer_data)
        return self.purchases.create(buyer_data, product, account, **extra_fields)

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

    @jsoned
    def caravan_products(self, hash_code):
        result = self.service.caravan_products(hash_code)
        return JsonFor(result).using('ProductJsonSerializer'), 200
