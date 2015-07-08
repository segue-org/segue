import flask
from flask import request, url_for
from flask.ext.jwt import current_user

from datetime import datetime
from segue.core import db

from segue.caravan.errors import InvalidCaravan
from segue.purchase.services import PurchaseService
from segue.caravan.services import CaravanService
from segue.caravan.models import CaravanProduct
from segue.proposal.services import NonSelectionService

from models import Product, PromoCodeProduct
from errors import ProductExpired, NoSuchProduct

DEFAULT_ORDERING = Product.sold_until

class ProductService(object):
    def __init__(self, db_impl=None, purchases=None, caravans=None, non_selection=None):
        self.db            = db_impl or db
        self.purchases     = purchases or PurchaseService()
        self.caravans      = caravans or CaravanService()
        self.non_selection = non_selection or NonSelectionService()

    def _in_time(self):
        return Product.sold_until >= datetime.now()

    def _is_public(self):
        return Product.public == True

    def list(self):
        return Product.query.filter(self._in_time(), self._is_public()).order_by(DEFAULT_ORDERING).all()

    def caravan_products(self, hash_code):
        return CaravanProduct.query.filter(self._in_time()).order_by(DEFAULT_ORDERING).all()

    def proponent_products(self, hash_code):
        notice = self.non_selection.get_by_hash(hash_code)
        if not notice: raise NoSuchProduct()

        return self.non_selection.products_for(notice.account)

    def promocode_products(self):
        return PromoCodeProduct.query.filter(self._in_time()).all()

    def get_product(self, product_id, strict=False):
        product = Product.query.get(product_id)
        if product: return product
        if strict: raise NoSuchProduct()
        return None

    def purchase(self, buyer_data, product_id, account=None):
        product = self.get_product(product_id)
        product.check_eligibility(buyer_data, account=account)
        extra_fields = product.extra_purchase_fields_for(buyer_data)
        return self.purchases.create(buyer_data, product, account, **extra_fields)

    def cheapest_for(self, category, account=None):
        candidates = Product.query.filter(Product.category == category).order_by(Product.price)
        if not candidates: raise NoSuchProduct()

        if not account: return candidates.first()

        eligible = filter(lambda p: p.check_eligibility({}, account), candidates)
        if not eligible: raise NoSuchProduct()

        return eligible[0]
