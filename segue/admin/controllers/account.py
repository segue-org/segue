import json

from flask import request, abort
from flask.ext.jwt import current_user

from segue.decorators import jwt_only, admin_only, jsoned
from segue.account.services import AccountService
from segue.purchase.services import PurchaseService

from ..responses import AccountDetailResponse

class AdminAccountController(object):
    def __init__(self, accounts=None, purchases=None):
        self.accounts     = accounts or AccountService()
        self.purchases    = purchases or PurchaseService()
        self.current_user = current_user

    @jwt_only
    @admin_only
    @jsoned
    def create(self):
        data = json.loads(request.data)
        result = self.accounts.create(data, rules='admin_create')
        return AccountDetailResponse.create(result), 200

    @jwt_only
    @admin_only
    @jsoned
    def modify(self, account_id):
        data = request.get_json()
        result = self.accounts.modify(account_id, data, by=self.current_user, allow_email_change=True) or flask.abort(404)
        return result, 200

    @jsoned
    @jwt_only
    @admin_only
    def list(self):
        criteria = request.args.get('q')
        result = self.accounts.lookup(criteria)[:20]
        return AccountDetailResponse.create(result), 200

    @jsoned
    @jwt_only
    @admin_only
    def get_one(self, account_id=None):
        result = self.accounts.get_one(account_id, check_owner=False) or abort(404)
        return AccountDetailResponse(result), 200

    @jsoned
    @jwt_only
    @admin_only
    def get_by_purchase(self, purchase_id=None):
        result = self.purchases.get_one(purchase_id, by=self.current_user) or abort(404)
        return AccountDetailResponse(result.customer), 200
