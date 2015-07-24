import re
import datetime

from sqlalchemy_utils.types.password import PasswordType
from sqlalchemy.sql import functions as func

from ..json import JsonSerializable, SQLAlchemyJsonSerializer
from ..core import db

import schema

class AccountJsonSerializer(SQLAlchemyJsonSerializer):
    _serializer_name = 'normal'
    def hide_field(self, child):
        return child == 'password'

    def serialize_child(self, child):
        return False

class SafeAccountJsonSerializer(AccountJsonSerializer):
    _serializer_name = 'safe'
    def hide_field(self, child):
        return child in [ 'password','email', 'role', 'phone', 'city', 'document' ]

class TokenJsonSerializer(AccountJsonSerializer):
    _serializer_name = 'token'
    def hide_field(self, child):
        return child not in [ 'id','email','role', 'name' ]

class Account(JsonSerializable, db.Model):
    _serializers = [ AccountJsonSerializer, SafeAccountJsonSerializer, TokenJsonSerializer ]

    id               = db.Column(db.Integer, primary_key=True)
    email            = db.Column(db.Text, unique=True)
    name             = db.Column(db.Text)
    badge_name       = db.Column(db.Text)
    password         = db.Column(PasswordType(schemes=['pbkdf2_sha512']))
    role             = db.Column(db.Enum(*schema.ACCOUNT_ROLES, name='account_roles'))
    document         = db.Column(db.Text)
    country          = db.Column(db.Text)
    state            = db.Column(db.Text)
    city             = db.Column(db.Text)
    phone            = db.Column(db.Text)
    organization     = db.Column(db.Text)
    resume           = db.Column(db.Text)
    certificate_name = db.Column(db.Text)

    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    corporate_id = db.Column(db.Integer)

    proposals       = db.relationship("Proposal", backref="owner")
    purchases       = db.relationship("Purchase", backref="customer")
    caravan_owned   = db.relationship("Caravan",  backref="owner")
    corporate_owned = db.relationship("Corporate", backref="owner", primaryjoin='Account.id==Corporate.owner_id')

    resets = db.relationship("ResetPassword", backref="account")

    def can_be_acessed_by(self, alleged):
        if not alleged: return False
        if self.id == alleged.id: return True
        return alleged.role in ('admin','frontdesk','cashier')

    def __repr__(self):
        return "<[{}]-{}-({})>".format(self.id, self.email, self.role)

    @property
    def can_receive_money(self):
        return self.role in ['admin','cashier']

    @property
    def is_speaker(self):
        return any([ x.is_talk for x in self.all_related_proposals ])

    @property
    def is_corporate(self):
        return self.corporate != None and self.corporate.kind == 'business';

    @property
    def is_government(self):
        return self.corporate != None and self.corporate.kind == 'government';

    @property
    def presented_talks(self):
        return filter(lambda x: x.was_presented, self.all_related_proposals)

    @property
    def has_presented(self):
        return len(self.presented_talks) > 0

    @property
    def all_related_proposals(self):
        as_coauthor = [ x.proposal for x in self.proposal_invites if x.accepted ]
        as_owner    = self.proposals

        return as_owner + as_coauthor

    @property
    def is_proponent(self):
        proposals = self.all_related_proposals
        if not proposals: return False
        return all([ not x.is_talk for x in proposals ])

    @property
    def identifier_purchase(self):
        if not self.purchases: return None
        valid_purchases = filter(lambda p:p.satisfied, self.purchases)
        if valid_purchases: return valid_purchases[-1]

        payable_purchases = filter(lambda p:p.payable, self.purchases)
        if payable_purchases: return payable_purchases[-1]

        return self.purchases[-1]

    @property
    def guessed_category(self):
        purchase = self.identifier_purchase
        if purchase: return purchase.product.category
        if not self.is_brazilian: return 'foreigner'
        if self.is_proponent: return 'proponent'
        return 'normal'

    @property
    def last_buyer(self):
        purchase = self.identifier_purchase
        if not purchase: return None
        return purchase.buyer

    @property
    def payments(self):
        payments = []
        for purchase in self.purchases:
            payments.extend(purchase.payments)
        return payments

    @property
    def has_valid_purchases(self):
        return any([ p.satisfied for p in self.purchases ])

    @property
    def has_valid_corporate_purchases(self):
        return any([ p.satisfied for p in self.purchases if p.kind == 'corporate' ])

    @property
    def payments(self):
        payments = []
        for purchase in self.purchases:
            payments.extend(purchase.payments)
        return payments

    @property
    def is_brazilian(self):
        return re.match(r"bra.*", self.country or '', re.IGNORECASE) != None

class ResetPassword(JsonSerializable, db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    hash         = db.Column(db.String(64))
    account_id   = db.Column(db.Integer, db.ForeignKey('account.id'))
    spent        = db.Column(db.Boolean, default=False)
    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)

class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    cctld = db.Column(db.Text)
    iso = db.Column(db.Integer)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.Text)
    name = db.Column(db.Text)
    latitude = db.Column(db.Numeric)
    longitude = db.Column(db.Numeric)

    __tablename__ = 'cities'
