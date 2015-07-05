from datetime import datetime
from ..json import JsonSerializable, SQLAlchemyJsonSerializer
from ..core import db

from errors import ProductExpired
from segue.corporate.models import CorporatePurchase

class ProductJsonSerializer(SQLAlchemyJsonSerializer):
    _serializer_name = 'normal'

class Product(JsonSerializable, db.Model):
    _serializers      = [ ProductJsonSerializer ]
    id                = db.Column(db.Integer, primary_key=True)
    kind              = db.Column(db.Enum('ticket', 'swag', name="product_kinds"))
    category          = db.Column(db.Text)
    public            = db.Column(db.Boolean, default=True)
    price             = db.Column(db.Numeric)
    sold_until        = db.Column(db.DateTime)
    description       = db.Column(db.Text)
    is_promo          = db.Column(db.Boolean, default=False, server_default='f')
    is_speaker        = db.Column(db.Boolean, default=False, server_default='f')
    gives_kit         = db.Column(db.Boolean, default=True,  server_default='t')
    can_pay_cash      = db.Column(db.Boolean, default=False, server_default='f')
    original_deadline = db.Column(db.DateTime)

    purchases  = db.relationship("Purchase", backref="product")

    __tablename__ = 'product'
    __mapper_args__ = { 'polymorphic_on': category, 'polymorphic_identity': 'normal' }

    def check_eligibility(self, buyer_data, account=None):
        if self.sold_until < datetime.now():
            raise ProductExpired()
        return True

    def extra_purchase_fields_for(self, buyer_data):
        return {}

    def special_purchase_class(self):
        return None

    def similar_products(self):
        return Product.query.filter(
                Product.category   == self.category,
                Product.kind       == self.kind,
                Product.sold_until >  datetime.now())

class StudentProduct(Product):
    __mapper_args__ = { 'polymorphic_identity': 'student' }

class PromoCodeProduct(Product):
    __mapper_args__ = { 'polymorphic_identity': 'promocode' }

    def check_eligibility(self, buyer_data, account=None):
        hash_code = buyer_data.get('hash_code',None)
        if not hash_code: return False

        promocode = PromoCode.query.filter(PromoCode.hash_code == hash_code).first()
        if not promocode: return False

        return promocode.product == self

class ForeignerProduct(Product):
    __mapper_args__ = { 'polymorphic_identity': 'foreigner' }

    def check_eligibility(self, buyer_data, account=None):
        if not account: return False
        return not account.is_brazilian

class ForeignerStudentProduct(ForeignerProduct):
    __mapper_args__ = { 'polymorphic_identity': 'foreigner-student' }

class CorporateProduct(Product):
    __mapper_args__ = { 'polymorphic_identity': 'business' }

    def special_purchase_class(self):
        return CorporatePurchase

class GovernmentProduct(Product):
    __mapper_args__ = { 'polymorphic_identity': 'government' }

    def special_purchase_class(self):
        return CorporatePurchase
