from datetime import datetime
from sqlalchemy.sql import functions as func
from segue.core import db, config

class SurveyAnswer(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    answer      = db.Column(db.Text)
    survey      = db.Column(db.Text)
    question    = db.Column(db.Text)
    account_id  = db.Column(db.Integer, db.ForeignKey('account.id'))

    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.now)

    account  = db.relationship('Account',  backref=db.backref('survey_answers', uselist=True, lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('account_id', 'question', name='UK_account_question'),
    )

class Question(object):
    def __init__(self, order, description, label, *options):
        self.order       = order
        self.description = description
        self.label       = label
        self.options     = filter(lambda x: len(x), options)

