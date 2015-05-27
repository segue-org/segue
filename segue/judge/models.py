from datetime import datetime
from sqlalchemy.sql import functions as func

from ..core import db
from segue.proposal.models import Proposal

class Judge(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    hash          = db.Column(db.String(64))
    votes         = db.Column(db.Integer, default=5)
    email         = db.Column(db.Text)
    created       = db.Column(db.DateTime, default=func.now())
    last_updated  = db.Column(db.DateTime, onupdate=datetime.now)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))

    matches = db.relationship("Match", backref="judge", lazy="dynamic")

    @property
    def spent(self):
        return self.matches.filter(Match.result != None).count()

    @property
    def remaining(self):
        return self.votes - self.matches.filter(Match.result != None).count()

class Match(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    result     = db.Column(db.Enum("player1", "player2", "tie", name="proposal_levels"))
    round      = db.Column(db.Integer)

    judge_id      = db.Column(db.Integer, db.ForeignKey('judge.id'))
    player2_id    = db.Column(db.Integer, db.ForeignKey('proposal.id'))
    player1_id    = db.Column(db.Integer, db.ForeignKey('proposal.id'))
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))

    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.now)

    def points_for(self, proposal):
        if not self.result: return 0
        if proposal == self.player1:
            if self.result == 'player1': return 3
            if self.result == 'tie': return 1
            return 0
        elif proposal == self.player2:
            if self.result == 'player2': return 3
            if self.result == 'tie': return 1
            return 0
        return 0


class Tournament(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    current_round = db.Column(db.Integer, default = 0)
    name          = db.Column(db.Text)
    selection     = db.Column(db.Text)
    status        = db.Column(db.Enum("open", "closed", name="proposal_levels"))

    judges  = db.relationship("Judge", backref="tournament", lazy='dynamic')
    matches = db.relationship("Match", backref="tournament", lazy="dynamic")

    @property
    def proposals(self):
        return Proposal.query.all()



