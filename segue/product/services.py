import flask
from flask import request, url_for
from flask.ext.jwt import current_user

from datetime import datetime
from segue.core import db

from segue.caravan.errors import InvalidCaravan
from segue.purchase.services import PurchaseService
from segue.caravan.services import CaravanService
from segue.caravan.models import CaravanProduct

from models import Product
from errors import ProductExpired

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
        product.check_eligibility(buyer_data, account=account)
        extra_fields = product.extra_purchase_fields_for(buyer_data)
        return self.purchases.create(buyer_data, product, account, **extra_fields)


