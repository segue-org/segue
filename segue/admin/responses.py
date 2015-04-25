from flask import url_for
from segue.json import SimpleJson

class DetailResponse(SimpleJson):
    @classmethod
    def create(cls, list_or_entity, *args, **kw):
        if isinstance(list_or_entity, list):
            return [ cls(e, *args, **kw) for e in list_or_entity ]
        cls(list_or_entity, *args, **kw)

    def __init__(self):
        self.__dict__["$type"] = self.__class__.__name__

    def add_link(self, name, collection, route='', **route_parms):
        if not hasattr(self, 'links'):
            self.links = {}
        self.links[name] = dict(
            count=len(collection),
            href =url_for(route, **route_parms)
        )


class AccountDetailResponse(DetailResponse):
    def __init__(self, account, links=True):
        super(AccountDetailResponse, self).__init__()
        self.name     = account.name
        self.email    = account.email
        self.id       = account.id
        self.document = account.document

        if links:
            self.add_link('proposals', account.proposals,     'admin.list_proposals', owner_id   =account.id)
            self.add_link('purchases', account.purchases,     'admin.list_purchases', customer_id=account.id)
            self.add_link('payments',  account.payments,      'admin.list_payments',  customer_id=account.id)
            self.add_link('caravans',  account.caravan_owned, 'admin.list_caravans',  owner_id   =account.id)

class ProposalDetailResponse(DetailResponse):
    def __init__(self, proposal):
        self.title        = proposal.title
        self.full         = proposal.full
        self.level        = proposal.level
        self.language     = proposal.language
        self.created      = proposal.created
        self.last_updated = proposal.last_updated

        self.owner   = AccountDetailResponse(proposal.owner, links=False)
        # self.invites = AccountDetailResponse(proposal.invies, links=False)
