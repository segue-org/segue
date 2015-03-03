import datetime

from ..json import JsonSerializable, SQLAlchemyJsonSerializer
from ..core import db

import schema

class ProductJsonSerializer(SQLAlchemyJsonSerializer):
    _serializer_name = 'normal'

class Product(JsonSerializable, db.Model):
    _serializers = [ ProductJsonSerializer ]
    id         = db.Column(db.Integer, primary_key=True)
    kind       = db.Column(db.Enum('ticket', 'swag'))
    category   = db.Column(db.Text)
    expiration = db.Column(db.DateTime)
    public     = db.Column(db.Boolean, default=True)
    price      = db.Column(db.Numeric)

class Purchase(JsonSerializable, db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    product_id  = db.Column(db.Integer, db.ForeignKey('product.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    status      = db.Column(db.Text)
