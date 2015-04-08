from segue.core import db
from segue.errors import AccountAlreadyHasCaravan, NotAuthorized

import schema

from models import Caravan
from factories import CaravanFactory

class CaravanService(object):
    def __init__(self):
        pass

    def get_one(self, caravan_id, by=None):
        result = Caravan.query.get(caravan_id)
        if self._check_ownership(result, by):
            return result
        raise NotAuthorized()

    def _check_ownership(self, entity, alleged):
        return entity and alleged and entity.owner == alleged

    def get_by_owner(self, owner):
        return Caravan.query.filter(Caravan.owner == owner).first()

    def create(self, data, owner):
        if self.get_by_owner(owner): raise AccountAlreadyHasCaravan()

        caravan = CaravanFactory.from_json(data, schema.create)
        caravan.owner = owner
        db.session.add(caravan)
        db.session.commit()
        return caravan


