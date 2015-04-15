from functools import wraps

from flask import request, url_for
from flask.ext.jwt import current_user

from ..errors import NotAuthorized
from ..core import jwt_required, config, logger
from ..json import jsoned, SimpleJson

from segue.account import AccountService
from segue.proposal import ProposalService

from responses import AccountDetailResponse, ProposalDetailResponse

def admin_only(fn):
    @wraps(fn)
    def wrapped(instance, *args, **kw):
        if instance.current_user.role != 'admin':
            logger.info("denied access to admin-only endpoint: %s", instance.current_user.__dict__)
            raise NotAuthorized()
        return fn(instance, *args, **kw)
    return wrapped

class AccountDetailResponse(SimpleJson):
    @classmethod
    def create(cls, list_or_entity):
        if isinstance(list_or_entity, list):
            return [ cls(e) for e in list_or_entity ]
        cls(list_or_entity)

    def add_link(self, name, collection, route='', **route_parms):
        if not hasattr(self, 'links'):
            self.links = {}
        self.links[name] = dict(
            count=len(collection),
            href =url_for(route, **route_parms)
        )

    def __init__(self, entity):
        self.name = entity.name
        self.email = entity.email
        self.id = entity.id
        self.add_link('proposals', entity.proposals, 'admin.proposals', owner_id   =entity.id)
        self.add_link('caravans',  entity.proposals, 'admin.caravans',  owner_id   =entity.id)
        self.add_link('purchases', entity.purchases, 'admin.purchases', customer_id=entity.id)
        self.add_link('payments',  entity.payments,  'admin.payments',  customer_id=entity.id)

class AdminController(object):
    def __init__(self, accounts=None, proposals=None):
        self.accounts = accounts or AccountService()
        self.proposals = proposals or ProposalService()
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
        result = self.accounts.get_one(account_id, check_owner=False)
        return AccountDetailResponse(result), 200

    @jwt_required()
    @admin_only
    @jsoned
    def list_proposals(self):
        parms = request.args.to_dict()
        result = self.proposals.query(as_user=self.current_user, **parms)
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
        return [], 200

    @jwt_required()
    @admin_only
    @jsoned
    def list_caravans(self):
        return [], 200

    @jwt_required()
    @admin_only
    @jsoned
    def list_payments(self):
        return [], 200
