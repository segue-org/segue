import datetime
from sqlalchemy.sql import functions as func
from ..core import db
from ..json import JsonSerializable
from segue.product.models import Product
from segue.purchase.models import Purchase
from segue.errors import WrongBuyerForProduct

from serializers import *

class Caravan(JsonSerializable, db.Model):
    _serializers = [ CaravanJsonSerializer ]
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.Text)
    city         = db.Column(db.Text)
    description  = db.Column(db.Text)
    owner_id     = db.Column(db.Integer, db.ForeignKey('account.id'))
    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)

    invites      = db.relationship("CaravanInvite", backref="caravan")
    riders       = db.relationship("CaravanRiderPurchase", backref="caravan", lazy='dynamic')

    @property
    def paid_riders(self):
        return self.riders.filter(Purchase.status == 'paid')

class CaravanInvite(JsonSerializable, db.Model):
    _serializers = [ CaravanInviteJsonSerializer, ShortCaravanInviteJsonSerializer ]

    id           = db.Column(db.Integer, primary_key=True)
    hash         = db.Column(db.String(64))
    caravan_id   = db.Column(db.Integer, db.ForeignKey('caravan.id'))
    recipient    = db.Column(db.Text)
    name         = db.Column(db.Text)
    account      = db.Column(db.Integer, db.ForeignKey('account.id'))
    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    status       = db.Column(db.Enum('pending','accepted','declined', 'cancelled', name='caravan_invite_statuses'),default='pending')

class CaravanRiderPurchase(Purchase):
    __mapper_args__ = { 'polymorphic_identity': 'caravan-rider' }
    caravan_id = db.Column(db.Integer, db.ForeignKey('caravan.id'), name='cr_caravan_id')

class CaravanLeaderPurchase(CaravanRiderPurchase):
    __mapper_args__ = { 'polymorphic_identity': 'caravan-leader' }

class CaravanProduct(Product):
    __mapper_args__ = { 'polymorphic_identity': 'caravan' }

    def special_purchase_class(self):
        return CaravanRiderPurchase

    def check_eligibility(self, buyer_data):
        super(CaravanProduct, self).check_eligibility(buyer_data)
        invites = CaravanInvite.query.filter(CaravanInvite.hash == buyer_data['caravan_invite_hash']).all()
        if not invites:
            raise WrongBuyerForProduct()

    def extra_purchase_fields_for(self, buyer_data):
        invite = CaravanInvite.query.filter(CaravanInvite.hash == buyer_data['caravan_invite_hash']).first()
        return { 'caravan': invite.caravan }
