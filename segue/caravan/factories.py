from segue.factory import Factory

from models import Caravan, CaravanInvite

class CaravanFactory(Factory):
    model = Caravan

    @classmethod
    def clean_for_update(self, data):
        return data

class CaravanInviteFactory(Factory):
    model = CaravanInvite
