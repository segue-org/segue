import datetime

from sqlalchemy.sql import functions as func
from ..json import JsonSerializable, SQLAlchemyJsonSerializer
from ..core import db

from sqlalchemy.ext.mutable import MutableDict

class BuyerJsonSerializer(SQLAlchemyJsonSerializer):
    _serializer_name = 'normal'

class Buyer(JsonSerializable, db.Model):
    _serializers = [ BuyerJsonSerializer ]
    id              = db.Column(db.Integer, primary_key=True)
    kind            = db.Column(db.Enum('person','company','government', name="buyer_kinds"))
    name            = db.Column(db.Text)
    document        = db.Column(db.Text)
    contact         = db.Column(db.Text)
    address_street  = db.Column(db.Text)
    address_number  = db.Column(db.Text)
    address_extra   = db.Column(db.Text)
    address_zipcode = db.Column(db.Text)
    address_city    = db.Column(db.Text)
    address_country = db.Column(db.Text)
    purchases       = db.relationship('Purchase', backref='buyer')

class PurchaseJsonSerializer(SQLAlchemyJsonSerializer):
    _serializer_name = 'normal'

class Purchase(JsonSerializable, db.Model):
    _serializers = [ PurchaseJsonSerializer ]
    id             = db.Column(db.Integer, primary_key=True)
    product_id     = db.Column(db.Integer, db.ForeignKey('product.id'))
    customer_id    = db.Column(db.Integer, db.ForeignKey('account.id'))
    buyer_id       = db.Column(db.Integer, db.ForeignKey('buyer.id'))
    status         = db.Column(db.Text, default='pending')
    created        = db.Column(db.DateTime, default=func.now())
    last_updated   = db.Column(db.DateTime, onupdate=datetime.datetime.now)

