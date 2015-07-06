from segue.core import config

from flask import request, abort, redirect
from flask.ext.jwt import current_user
from segue.decorators import jwt_only, frontdesk_only, jsoned, accepts_html

from services import BadgeService, PeopleService
from responses import PersonResponse, BuyerResponse, ProductResponse, PaymentResponse, ReceptionResponse

class ReceptionController(object):
    def __init__(self, people=None):
        self.people = people or PeopleService()

    @jsoned
    @accepts_html
    def get_by_hash(self, hash_code=None, wants_html=False):
        person = self.people.get_by_hash(hash_code) or flask.abort(404)
        if wants_html:
            path = '/#/reception/{}'.format(hash_code)
            return redirect(config.FRONTEND_URL + path)
        else:
            return ReceptionResponse.create(person), 200

class PersonController(object):
    def __init__(self, people=None, badges=None):
        self.people = people or PeopleService()
        self.badges = badges or BadgeService()
        self.current_user = current_user

    @jwt_only
    @frontdesk_only
    @jsoned
    def list(self):
        needle = request.args.get('q')
        result = self.people.lookup(needle, by_user=self.current_user)
        return PersonResponse.create(result, links=False), 200

    @jwt_only
    @frontdesk_only
    @jsoned
    def get_one(self, person_id):
        result = self.people.get_one(person_id, by_user=self.current_user)
        return PersonResponse.create(result, links=True, embeds=True), 200

    @jwt_only
    @frontdesk_only
    @jsoned
    def patch(self, person_id):
        data = request.get_json()
        result = self.people.patch(person_id, by_user=self.current_user, **data)
        return PersonResponse.create(result, links=True), 200

    @jwt_only
    @frontdesk_only
    @jsoned
    def create(self):
        email = request.get_json().get('email',None)
        if not email: abort(400)
        result = self.people.create(email, by_user=self.current_user)
        return PersonResponse.create(result, links=True), 200

    def apply_promo(self, person_id):
        pass
    def make_payment(self, person_id):
        pass
    def set_product(self, person_id):
        pass

    @jwt_only
    @frontdesk_only
    @jsoned
    def eligible(self, person_id):
        result = self.people.get_one(person_id, by_user=self.current_user) or abort(404)
        return ProductResponse.create(result.eligible_products), 200

    @jwt_only
    @frontdesk_only
    @jsoned
    def buyer(self, person_id):
        result = self.people.get_one(person_id, by_user=self.current_user) or abort(404)
        return BuyerResponse.create(result.buyer), 200

    @jwt_only
    @frontdesk_only
    @jsoned
    def related(self, person_id):
        result = self.people.get_one(person_id, by_user=self.current_user) or abort(404)
        return PersonResponse.create(result.related_people, links=False), 200

    def get_badge(self, person_id):
        pass

    @jwt_only
    @frontdesk_only
    @jsoned
    def create_badge(self, person_id):
        person = self.people.get_one(person_id, by_user=self.current_user)
        result = self.badges.make_badge_for_person("vagrant", person, by_user=self.current_user)
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
