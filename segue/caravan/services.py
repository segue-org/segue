from segue.core import db

import schema

from models import Caravan
from factories import CaravanFactory

class CaravanService(object):
    def __init__(self):
        pass

    def get_one(self, caravan_id):
        return Caravan.query.get(caravan_id)

    def create(self, data, owner):
        caravan = CaravanFactory.from_json(data, schema.create)
        caravan.owner = owner
        db.session.add(caravan)
        db.session.commit()
        return caravan


