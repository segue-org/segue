import flask
from flask.ext.jwt import current_user
from flask import request

from segue.json import JsonFor
from segue.core import config
from segue.decorators import jsoned, jwt_only

from services import PurchaseService, PaymentService
from factories import PurchaseFactory

import schema

class PurchaseController(object):
    def __init__(self, service=None):
        self.service = service or PurchaseService()
        self.current_user = current_user

    @jsoned
    @jwt_only
    def list(self):
        parms = { c: request.args.get(c) for c in PurchaseFactory.QUERY_WHITELIST if c in request.args }
        result = self.service.query(by=self.current_user, **parms)
        return JsonFor(result).using('PurchaseJsonSerializer'), 200

    @jwt_only
    @jsoned
    def get_one(self, purchase_id=None):
        result = self.service.get_one(purchase_id, by=self.current_user) or flask.abort(404)
        return result, 200

    @jwt_only
    @jsoned
    def pay(self, purchase_id=None, method=None):
        payload = request.get_json()
        result = self.service.create_payment(purchase_id, method, payload, by=self.current_user)
        return result, 200

    @jsoned
    def schema(self, name):
        return schema.whitelist[name], 200

    @jwt_only
    @jsoned
    def clone(self, purchase_id=None):
        result = self.service.clone_purchase(purchase_id, by=self.current_user) or flask.abort(404)
        return result, 200

class PaymentController(object):
    def __init__(self, service=None):
        self.service = service or PaymentService()

    @jsoned
    def notify(self, purchase_id=None, payment_id=None):
        payload = request.form.to_dict(True)
        result = self.service.notify(purchase_id, payment_id, payload) or flask.abort(404)
        return result[0], 200

    def conclude(self, purchase_id, payment_id):
        payload = request.args.to_dict(True)
        self.service.conclude(purchase_id, payment_id, payload) or flask.abort(404)
        path = '/#/purchase/{}/payment/{}/conclude'.format(purchase_id, payment_id)
        return flask.redirect(config.FRONTEND_URL + path)
