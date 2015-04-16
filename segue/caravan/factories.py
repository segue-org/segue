import schema
from segue.factory import Factory
from models import Caravan, CaravanInvite, CaravanLeaderPurchase

class CaravanFactory(Factory):
    model = Caravan

    UPDATE_WHITELIST = schema.edit_caravan["properties"].keys()

    @classmethod
    def clean_for_update(self, data):
        return { c:v for c,v in data.items() if c in CaravanFactory.UPDATE_WHITELIST }

class CaravanInviteFactory(Factory):
    model = CaravanInvite

class CaravanLeaderPurchaseFactory(Factory):
    model = CaravanLeaderPurchase

    @classmethod
    def create(cls, caravan):
        result = cls.model()
        result.caravan  = caravan
        result.status   = 'paid'
        result.customer = caravan.owner
        return result
