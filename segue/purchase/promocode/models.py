from segue.core import db
from ..models import Payment, Transition
from segue.json import JsonSerializable

class PromoCode(JsonSerializable, db.Model):
    # 1 - EXPOSITOR
    # 2 - PATROCINADOR
    # 3 - CORTESIA c/kit
    # 4 - CORTESIA s/kit
    # 5 - COMUNIDADES
    # 6 - ASSOCIADOS
    # 7 - CONVIDADOS
    # 8 - ESPECIAL

    id             = db.Column(db.Integer, primary_key=True)
    creator_id     = db.Column(db.Integer, db.ForeignKey('account.id'))
    product_id     = db.Column(db.Integer, db.ForeignKey('product.id'))
    hash_code      = db.Column(db.String(32))
    description    = db.Column(db.Text)
    discount       = db.Column(db.Numeric)

    creator        = db.relationship('Account')
    product        = db.relationship('Product', backref='promocodes')
    payment        = db.relationship('PromoCodePayment', backref=db.backref('promocode', uselist=False))

    @property
    def used(self):
        return self.payment is not None

class PromoCodePayment(Payment):
    __mapper_args__ = { 'polymorphic_identity': 'promocode' }

    promocode_id     = db.Column(db.Integer, db.ForeignKey('promocode.id'), name='pc_promocode_id')


class PromoCodeTransition(Transition):
    __mapper_args__ = { 'polymorphic_identity': 'promocode' }
