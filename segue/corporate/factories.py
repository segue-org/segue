import schema
from segue.factory import Factory
from models import Corporate, CorporateEmployee, CorporatePurchase, EmployeePurchase

class CorporateFactory(Factory):
    model = Corporate

    UPDATE_WHITELIST = schema.edit_corporate["properties"].keys()

    @classmethod
    def clean_for_update(self, data):
        return { c:v for c,v in data.items() if c in CorporateFactory.UPDATE_WHITELIST }

class CorporateEmployeeFactory(Factory):
    model = CorporateEmployee

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
    def create(cls, corporate):
        result = cls.model()
        result.corporate  = corporate
        result.status   = 'pending'
        result.customer = corporate.owner
        return result
