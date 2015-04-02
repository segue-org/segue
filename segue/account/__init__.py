import flask
from flask import request, url_for, redirect
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from flask.ext.jwt import current_user

from ..core import db, jwt_required
from ..factory import Factory
from ..json import jsoned
from ..errors import InvalidLogin, EmailAlreadyInUse, NotAuthorized

from jwt import Signer

from models import Account
from services import AccountService
import schema


class AccountController(object):
    def __init__(self, service=None):
        self.service = service or AccountService()
        self.current_user = current_user

    @jwt_required()
    @jsoned
    def get_one(self, account_id):
        result = self.service.get_one(account_id, by=self.current_user) or flask.abort(404)
        return result, 200

    @jwt_required()
    @jsoned
    def modify(self, account_id):
        data = request.get_json()
        result = self.service.modify(account_id, data, by=self.current_user) or flask.abort(404)
        return result, 200

    @jsoned
    def schema(self, name):
        return schema.whitelist[name]

    @jsoned
    def create(self):
        data = request.get_json()
        return self.service.create(data), 201

    @jsoned
    def login(self):
        data = request.get_json()
        return self.service.login(**data), 200

    def list_proposals(self, account_id):
        query_string = "?owner_id={}".format(account_id)
        return redirect(url_for('proposals.list') + query_string)

    def list_purchases(self, account_id):
        query_string = "?customer_id={}".format(account_id)
        return redirect(url_for('purchases.list') + query_string)

    def get_caravan(self, account_id):
        query_string = "?owner_id={}".format(account_id)
        return redirect(url_for('caravans.get_one') + query_string)
