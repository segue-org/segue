from flask import request, abort
from flask.ext.jwt import current_user
from segue.decorators import jwt_only, frontdesk_only, jsoned
from services import BadgeService

class PersonController(object):
    def list(self):
        pass
    def create(self):
        pass
    def get_one(self, person_id):
        pass
    def modify(self, person_id):
        pass
    def apply_promo(self, person_id):
        pass
    def make_payment(self, person_id):
        pass
    def get_badge(self, person_id):
        pass
    def create_badge(self, person_id):
        pass

class BadgeController(object):
    def __init__(self, service=None):
        self.service      = service or BadgeService()
        self.current_user = current_user

    @jwt_only
    @frontdesk_only
    @jsoned
    def create(self):
        self.service.make_badge("vagrant","teste", by_user=self.current_user)
        return {}, 200

    def get_one(self, badge_id):
        pass

    def move(self, badge_id):
        pass

    def give(self, badge_id):
        pass

    def trash(self, badge_id):
        pass
