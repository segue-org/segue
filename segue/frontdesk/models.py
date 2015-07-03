from segue.core import db
from sqlalchemy.sql import functions as func

class Badge(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    person_id   = db.Column(db.Integer, db.ForeignKey('purchase.id'))
    issuer_id   = db.Column(db.Integer, db.ForeignKey('account.id'))
    name        = db.Column(db.Text)
    company     = db.Column(db.Text)
    city        = db.Column(db.Text)
    kind        = db.Column(db.Text)

    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.now)
