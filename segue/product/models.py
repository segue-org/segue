import datetime
from sqlalchemy.sql import functions as func

from ..json import JsonSerializable, SQLAlchemyJsonSerializer
from ..core import db

class ProductJsonSerializer(SQLAlchemyJsonSerializer):
    _serializer_name = 'normal'

class Product(JsonSerializable, db.Model):
    _serializers = [ ProductJsonSerializer ]
    id          = db.Column(db.Integer, primary_key=True)
    kind        = db.Column(db.Enum('ticket', 'swag', name="product_kinds"))
    category    = db.Column(db.Text)
    public      = db.Column(db.Boolean, default=True)
    price       = db.Column(db.Numeric)
    sold_until  = db.Column(db.DateTime)
    description = db.Column(db.Text)

    purchases  = db.relationship("Purchase", backref="product")

