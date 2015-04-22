import schema
from segue.factory import Factory
from models import Corporate, CorporateInvite, CorporateLeaderPurchase

class CorporateFactory(Factory):
    model = Corporate

    UPDATE_WHITELIST = schema.edit_corporate["properties"].keys()

    @classmethod
    def clean_for_update(self, data):
        return { c:v for c,v in data.items() if c in CorporateFactory.UPDATE_WHITELIST }

class CorporateInviteFactory(Factory):
    model = CorporateInvite

class CorporateLeaderPurchaseFactory(Factory):
    model = CorporateLeaderPurchase

    @classmethod
    def create(cls, corporate):
        result = cls.model()
        result.corporate  = corporate
        result.status   = 'paid'
        result.customer = corporate.owner
        return result
