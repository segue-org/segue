import schema
from segue.factory import Factory
from models import Corporate, CorporateAccount, CorporatePurchase, EmployeePurchase

class CorporateFactory(Factory):
    model = Corporate

    UPDATE_WHITELIST = schema.edit_corporate["properties"].keys()

    @classmethod
    def clean_for_update(self, data):
        return { c:v for c,v in data.items() if c in CorporateFactory.UPDATE_WHITELIST }

class CorporateAccountFactory(Factory):
    model = CorporateAccount

class CorporatePurchaseFactory(Factory):
    model = CorporatePurchase

    @classmethod
    def create(cls, corporate):
        result = cls.model()
        result.corporate  = corporate
        result.status   = 'paid'
        result.customer = corporate.owner
        return result

class EmployeePurchaseFactory(Factory):
    model = EmployeePurchase

    @classmethod
    def create(cls, corporate, account):
        result = cls.model()
        result.corporate  = corporate
        result.status   = 'pending'
        result.customer = account
        return result
