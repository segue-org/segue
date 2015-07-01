from flask import request, abort
from flask.ext.jwt import current_user

from segue.core import cache
from segue.decorators import jsoned, jwt_only, admin_only

from segue.purchase.promocode import PromoCodeService
from segue.product.services import ProductService

from ..responses import PromoCodeResponse, ProductDetailResponse

class AdminPromoCodeController(object):
    def __init__(self, promocodes=None, products=None):
        self.current_user = current_user
        self.promocodes   = promocodes or PromoCodeService()
        self.products     = products   or ProductService()

    @jwt_only
    @admin_only
    @jsoned
    def list_promocodes(self):
        parms = request.args.to_dict()
        result = self.promocodes.lookup(as_user=self.current_user, **parms)
        return PromoCodeResponse.create(result), 200

    @jwt_only
    @admin_only
    @jsoned
    def get_one(self, promocode_id):
        result = self.promocodes.get_one(promocode_id)
        return PromoCodeResponse.create(result), 200

    @jwt_only
    @admin_only
    @jsoned
    def get_products(self):
        result = self.products.promocode_products()
        return ProductDetailResponse.create(result), 200

    @jwt_only
    @admin_only
    @jsoned
    def create(self):
        data = request.get_json()
        product_id = data.pop('product_id',None) or abort(400)
        product = self.products.get_product(product_id, strict=True) or abort(404)
        result = self.promocodes.create(product, creator=self.current_user, **data)
        return PromoCodeResponse.create(result), 200
