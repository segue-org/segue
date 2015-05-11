from functools import wraps

from flask import request, url_for, abort
from flask.ext.jwt import current_user

from ..errors import NotAuthorized
from ..core import jwt_required, config, logger
from ..json import jsoned, SimpleJson

from segue.account import AccountService
from segue.proposal import ProposalService
from segue.purchase import PurchaseService, PaymentService

from responses import *

def admin_only(fn):
    @wraps(fn)
    def wrapped(instance, *args, **kw):
        if instance.current_user.role != 'admin':
            logger.info("denied access to admin-only endpoint: %s", instance.current_user.__dict__)
            raise NotAuthorized()
        return fn(instance, *args, **kw)
    return wrapped


class AdminController(object):
    def __init__(self, accounts=None, proposals=None, purchases=None, payments=None):
        self.accounts = accounts or AccountService()
        self.proposals = proposals or ProposalService()
        self.purchases = purchases or PurchaseService()
        self.payments = payments or PaymentService()
        self.current_user = current_user

    @jwt_required()
    @admin_only
    @jsoned
    def list_accounts(self):
        criteria = request.args.get('q')
        result = self.accounts.lookup(criteria)[:20]
        return AccountDetailResponse.create(result), 200

    @jwt_required()
    @admin_only
    @jsoned
    def get_account(self, account_id=None):
        result = self.accounts.get_one(account_id, check_owner=False) or abort(404)
        return AccountDetailResponse(result), 200

    @jwt_required()
    @admin_only
    @jsoned
    def list_proposals(self):
        parms = request.args.to_dict()
        result = self.proposals.lookup(as_user=self.current_user, **parms)
        return ProposalDetailResponse.create(result), 200

    @jwt_required()
    @admin_only
    @jsoned
    def get_proposal(self, proposal_id=None):
        result = self.proposals.get_one(proposal_id)
        return ProposalDetailResponse(result), 200

    @jwt_required()
    @admin_only
    @jsoned
    def list_purchases(self):
        parms = request.args.to_dict()
        result = self.purchases.query(as_user=self.current_user, **parms)
        return PurchaseDetailResponse.create(result), 200

    @jwt_required()
    @admin_only
    @jsoned
    def list_caravans(self):
        return [], 200

    @jwt_required()
    @admin_only
    @jsoned
    def list_payments(self):
        parms = request.args.to_dict()
        result = self.payments.query(as_user=self.current_user, **parms)
        return PaymentDetailResponse.create(result), 200
