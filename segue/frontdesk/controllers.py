from flask import request, abort
from flask.ext.jwt import current_user
from segue.decorators import jwt_only, frontdesk_only, jsoned

from services import BadgeService, PeopleService
from responses import PersonResponse

class PersonController(object):
    def __init__(self, people=None, badges=None):
        self.people = people or PeopleService()
        self.badges = badges or BadgeService()
        self.current_user = current_user

    def list(self):
        pass
    def create(self):
        pass

    @jwt_only
    @frontdesk_only
    @jsoned
    def get_one(self, person_id):
        result = self.people.get_one(person_id, by_user=self.current_user)
        return PersonResponse.create(result), 200

    def modify(self, person_id):
        pass
    def apply_promo(self, person_id):
        pass
    def make_payment(self, person_id):
        pass
    def get_badge(self, person_id):
        pass

    @jwt_only
    @frontdesk_only
    @jsoned
    def create_badge(self, person_id):
        person = self.people.get_one(person_id)
        result = self.badges.make_badge("vagrant", person, by_user=self.current_user)
        return {},200

class BadgeController(object):
    def __init__(self, badges=None):
        self.badges       = badges or BadgeService()
        self.current_user = current_user

    def get_one(self, badge_id):
        pass

    def move(self, badge_id):
        pass

    def give(self, badge_id):
        pass

    def trash(self, badge_id):
        pass
