import flask
from flask.ext.jwt import current_user
from flask import request

from ..json import jsoned, JsonFor
from ..core import jwt_required

from services import PurchaseService, PaymentService
from factories import PurchaseFactory

import schema

class PurchaseController(object):
    def __init__(self, service=None):
        self.service = service or PurchaseService()
        self.current_user = current_user

    @jsoned
    @jwt_required()
    def list(self):
        parms = { c: request.args.get(c) for c in PurchaseFactory.QUERY_WHITELIST if c in request.args }
        result = self.service.query(by=self.current_user, **parms)
        return JsonFor(result).using('ShortPurchaseJsonSerializer'), 200

    @jwt_required()
    @jsoned
    def get_one(self, purchase_id=None):
        result = self.service.get_one(purchase_id, by=self.current_user) or flask.abort(404)
        return result, 200

    @jwt_required()
    @jsoned
    def pay(self, purchase_id=None, method=None):
        payload = request.get_json()
        result = self.service.create_payment(purchase_id, method, payload, by=self.current_user)
        return result, 200

    @jsoned
    def schema(self, name):
        return schema.whitelist[name], 200

class PaymentController(object):
    def __init__(self, service=None):
        self.service = service or PaymentService()

    @jsoned
    def notify(self, purchase_id=None, payment_id=None):
        notification_code = request.args.get('notificationCode', None)
        if not notification_code: flask.abort(400, "notificationCode is mandatory")

        result = self.service.notify(purchase_id, payment_id, notification_code) or flask.abort(404)
        return result, 200

    def conclude(self):
        pass


