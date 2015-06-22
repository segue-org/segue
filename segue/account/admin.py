from flask import request, abort

from segue.decorators import jwt_only, admin_only, jsoned
from segue.admin.controllers import BaseAdminController
from segue.admin.responses import AccountDetailResponse

from services import AccountService

class AdminAccountController(BaseAdminController):
    def __init__(self, service=None):
        super(AdminAccountController, self).__init__()
        self.service = service or AccountService()

    @jsoned
    @jwt_only
    @admin_only
    def list(self):
        criteria = request.args.get('q')
        result = self.service.lookup(criteria)[:20]
        return AccountDetailResponse.create(result), 200

    @jsoned
    @jwt_only
    @admin_only
    def get_one(self, account_id=None):
        result = self.service.get_one(account_id, check_owner=False) or abort(404)
        return AccountDetailResponse(result), 200
