from datetime import datetime
from sqlalchemy.sql import functions as func
from segue.core import db, config

class Prototype():
    def __init__(self, **kw):
        for key, value in kw.items():
            setattr(self, key, value)

    def is_like(self, cert):
        if isinstance(cert, Certificate):
            return cert.is_like(self)
        return self.__dict__ == cert.__dict__

    @property
    def descriptor(self):
        if hasattr(self,'talk'):
            return "speaker-{}".format(self.talk.id)
        return self.kind

    def __repr__(self):
        talk_id = self.talk.id if hasattr(self,'talk') else None

        return "<CertProto:({}):A{}:PU{}:T{}>".format(self.kind, self.account.id, self.ticket.id, talk_id)

class Certificate(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    kind         = db.Column(db.Text)
    name         = db.Column(db.Text)
    language     = db.Column(db.String(2))
    hash_code    = db.Column(db.String(10))
    ticket_id    = db.Column(db.Integer, db.ForeignKey('purchase.id'))
    account_id   = db.Column(db.Integer, db.ForeignKey('account.id'))
    issue_date   = db.Column(db.DateTime)

    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.now)

    account  = db.relationship('Account',  backref=db.backref('certificates', uselist=True, lazy='dynamic'))
    ticket   = db.relationship('Purchase', backref=db.backref('certificates', uselist=True, lazy='dynamic'))

    __tablename__ = 'certificate'
    __mapper_args__ = { 'polymorphic_on': kind, 'polymorphic_identity': 'certificate' }

    def is_like(self, prototype):
        return self.kind == prototype.kind and self.ticket == prototype.ticket and self.account == prototype.account

    def __repr__(self):
        return "<Cert:{}({}):A{}:PU{}>".format(self.id, self.kind, self.account_id, self.ticket_id)

    @property
    def template_vars(self):
        return { "NOME": self.name, "URL": self.url }

    @property
    def url(self):
        return "{}/{}".format(config.CERTIFICATES_URL, self.hash_code)

    @property
    def descriptor(self):
        return self.kind

class AttendantCertificate(Certificate):
    __mapper_args__ = { 'polymorphic_identity': 'attendant' }

    @property
    def template_file(self):
        return 'certificate/templates/attendant-{}.svg'.format(self.language)

class SpeakerCertificate(Certificate):
    __mapper_args__ = { 'polymorphic_identity': 'speaker' }

    talk_id = db.Column(db.Integer, db.ForeignKey('proposal.id'), name='sc_talk_id')
    talk    = db.relationship('Proposal', backref=db.backref('certificates', lazy='dynamic'))

    def is_like(self, prototype):
        return super(SpeakerCertificate, self).is_like(prototype) and self.talk == prototype.talk

    @property
    def template_file(self):
        return 'certificate/templates/speaker-{}.svg'.format(self.language)

    @property
    def template_vars(self):
        result = super(SpeakerCertificate, self).template_vars
        result['PALESTRA'] = self.talk.title
        return result

    @property
    def descriptor(self):
        return "speaker-{}".format(self.talk.id)
