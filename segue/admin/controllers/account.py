import json

from flask import request, abort
from flask.ext.jwt import current_user

from segue.decorators import jwt_only, admin_only, jsoned
from segue.account.services import AccountService

from ..responses import AccountDetailResponse

class AdminAccountController(object):
    def __init__(self, service=None):
        self.current_user = current_user
        self.service = service or AccountService()

    @jwt_only
    @admin_only
    @jsoned
    def create(self):
        data = json.loads(request.data)
        result = self.service.create(data, rules='admin_create')
        return AccountDetailResponse.create(result), 200

    @jwt_only
    @admin_only
    @jsoned
    def modify(self, account_id):
        data = request.get_json()
        result = self.service.modify(account_id, data, by=self.current_user, allow_email_change=True) or flask.abort(404)
        return result, 200

    @jsoned
    @jwt_only
    @admin_only
    def list(self):
        criteria = request.args.to_dict()
        result = self.service.lookup(by=self.current_user, **criteria)[:20]
        return AccountDetailResponse.create(result), 200

    @jsoned
    @jwt_only
    @admin_only
    def get_one(self, account_id=None):
        result = self.service.get_one(account_id, check_owner=False) or abort(404)
        return AccountDetailResponse(result), 200
