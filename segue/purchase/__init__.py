import flask
from flask.ext.jwt import current_user
from flask import request

from ..json import jsoned
from ..core import jwt_required

from services import PurchaseService, PaymentService

class PurchaseController(object):
    def __init__(self, service=None):
        self.service = service or PurchaseService()
        self.current_user = current_user

    def list(self):
        pass

    @jwt_required()
    @jsoned
    def get_one(self, purchase_id=None):
        result = self.service.get_one(purchase_id, by=self.current_user)
        return result, 200

    @jwt_required()
    @jsoned
    def pay(self, purchase_id=None, method=None):
        result = self.service.pay(purchase_id, method, by=self.current_user)
        return result, 200

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

