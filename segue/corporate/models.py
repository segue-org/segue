import datetime
from sqlalchemy.sql import functions as func
from ..core import db
from ..json import JsonSerializable
from segue.product.models import Product
from segue.purchase.models import Purchase
from segue.errors import WrongBuyerForProduct

from serializers import *

class Corporate(JsonSerializable, db.Model):
    _serializers = [ CorporateJsonSerializer ]
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.Text)
    city         = db.Column(db.Text)
    document     = db.Column(db.Text)
    owner_id     = db.Column(db.Integer, db.ForeignKey('account.id'))
    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)

    invites      = db.relationship("CorporateInvite", backref="corporate")
    riders       = db.relationship("CorporateRiderPurchase", backref="corporate", lazy='dynamic')

    @property
    def paid_riders(self):
        return self.riders.filter(Purchase.status == 'paid')

class CorporateInvite(JsonSerializable, db.Model):
    _serializers = [ CorporateInviteJsonSerializer, ShortCorporateInviteJsonSerializer ]

    id           = db.Column(db.Integer, primary_key=True)
    hash         = db.Column(db.String(64))
    corporate_id = db.Column(db.Integer, db.ForeignKey('corporate.id'))
    recipient    = db.Column(db.Text)
    name         = db.Column(db.Text)
    document     = db.Column(db.Text)
    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    status       = db.Column(db.Enum('pending','accepted','declined', 'cancelled', name='corporate_invite_statuses'),default='accepted')

class CorporateRiderPurchase(Purchase):
    __mapper_args__ = { 'polymorphic_identity': 'corporate-rider' }
    corporate_id = db.Column(db.Integer, db.ForeignKey('corporate.id'), name='cr_corporate_id')

class CorporateLeaderPurchase(CorporateRiderPurchase):
    __mapper_args__ = { 'polymorphic_identity': 'corporate-leader' }

class CorporateProduct(Product):
    __mapper_args__ = { 'polymorphic_identity': 'corporate' }

    def special_purchase_class(self):
        return CorporateRiderPurchase

    def check_eligibility(self, buyer_data):
        if not super(CorporateProduct, self).check_eligibility(buyer_data):
            raise WrongBuyerForProduct()

    def extra_purchase_fields_for(self, buyer_data):
        return {}