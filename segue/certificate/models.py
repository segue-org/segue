from datetime import datetime
from sqlalchemy.sql import functions as func
from segue.core import db

class Certificate(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    kind         = db.Column(db.Text)
    name         = db.Column(db.Text, nullable=False)
    language     = db.Column(db.String(2))
    hash_code    = db.Column(db.String(10))
    ticket_id    = db.Column(db.Integer, db.ForeignKey('purchase.id'))
    account_id   = db.Column(db.Integer, db.ForeignKey('account.id'))

    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.now)

    account  = db.relationship('Account',  backref=db.backref('certificates', uselist=True))
    ticket   = db.relationship('Purchase', backref=db.backref('certificate', uselist=False))

    __tablename__ = 'certificate'
    __mapper_args__ = { 'polymorphic_on': kind, 'polymorphic_identity': 'attendant' }

class AttendantCertificate(Certificate):
    __mapper_args__ = { 'polymorphic_identity': 'attendant' }

class SpeakerCertificate(Certificate):
    __mapper_args__ = { 'polymorphic_identity': 'speaker' }

    talk_id = db.Column(db.Integer, db.ForeignKey('proposal.id'), name='sc_talk_id')
    talk    = db.relationship('Proposal', backref='certificates')
