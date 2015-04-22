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
from segue.corporate.services import CorporateService
from segue.corporate.models import CorporateProduct

DEFAULT_ORDERING = Product.sold_until

class ProductService(object):
    def __init__(self, db_impl=None, purchases=None, caravans=None, corporates=None):
        self.db         = db_impl or db
        self.purchases  = purchases or PurchaseService()
        self.caravans   = caravans or CaravanService()
        self.corporates = corporates or CorporateService()

    def _in_time(self):
        return Product.sold_until >= datetime.now()

    def _is_public(self):
        return Product.public == True

    def list(self):
        return Product.query.filter(self._in_time(), self._is_public()).order_by(DEFAULT_ORDERING).all()

    def caravan_products(self, hash_code):
        return CaravanProduct.query.filter(self._in_time()).order_by(DEFAULT_ORDERING).all()

    def corporate_products(self):
        return CorporateProduct.query.filter(self._in_time()).order_by(DEFAULT_ORDERING).all()

    def get_product(self, product_id):
        return Product.query.get(product_id)

    def purchase(self, buyer_data, product_id, account=None):
        product = self.get_product(product_id)
        product.check_eligibility(buyer_data)
        extra_fields = product.extra_purchase_fields_for(buyer_data)
        return self.purchases.create(buyer_data, product, account, **extra_fields)

    def group_purchase(self, buyer_data, product_id, account=None):
        product = self.get_product(product_id)
        # product.check_eligibility(buyer_data)
        extra_fields = product.extra_purchase_fields_for(buyer_data)
        print "************* dados do group_purchase ***************************"
        print buyer_data
        print account
        print "************* /dados do group_purchase ***************************"
        multiplier = len(buyer_data[u'invites'])
        amount = multiplier * product.price
        #extra_fields['amount'] = amount
        
        for i in buyer_data[u'invites']:
            self.corporates.add_invite(int(buyer_data[u'corporate_id']), i, account)
        
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

    @jwt_required()
    @jsoned
    def group_purchase(self, product_id):
        data = request.get_json()
        result = self.service.group_purchase(data, product_id, account=self.current_user) or flask.abort(400)
        return result, 200

    @jsoned
    def caravan_products(self, hash_code):
        result = self.service.caravan_products(hash_code)
        return JsonFor(result).using('ProductJsonSerializer'), 200

    @jsoned
    def corporate_products(self):
        result = self.service.corporate_products()
        return JsonFor(result).using('ProductJsonSerializer'), 200
