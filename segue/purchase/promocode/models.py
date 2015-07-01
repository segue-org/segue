from segue.core import db
from ..models import Payment, Transition
from segue.json import JsonSerializable

class PromoCode(JsonSerializable, db.Model):
    __tablename__ = 'promocode'

    id             = db.Column(db.Integer, primary_key=True)
    creator_id     = db.Column(db.Integer, db.ForeignKey('account.id'))
    product_id     = db.Column(db.Integer, db.ForeignKey('product.id'))
    hash_code      = db.Column(db.String(32))
    description    = db.Column(db.Text)
    discount       = db.Column(db.Numeric)

    creator = db.relationship('Account')
    product = db.relationship('Product', backref='promocodes')
    payment = db.relationship('PromoCodePayment', uselist=False, backref=db.backref('promocode', uselist=False))

    @property
    def used(self):
        if isinstance(self.payment, list):
            return len(self.payment) > 0
        else:
            return False

class PromoCodePayment(Payment):
    __mapper_args__ = { 'polymorphic_identity': 'promocode' }

    promocode_id     = db.Column(db.Integer, db.ForeignKey('promocode.id'), name='pc_promocode_id')

    @property
    def paid_amount(self):
        valid = self.promocode != None
        total_value = self.purchase.product.price
        if valid:
            discounted  = self.promocode.discount * total_value
        return discounted if valid else 0

class PromoCodeTransition(Transition):
    __mapper_args__ = { 'polymorphic_identity': 'promocode' }
