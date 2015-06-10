from datetime import datetime, timedelta
from sqlalchemy.sql import functions as func

from ..core import db
from segue.proposal.models import Proposal, ProposalTag

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
    result     = db.Column(db.Enum("player1", "player2", "tie", name="match_results"))
    round      = db.Column(db.Integer)

    judge_id      = db.Column(db.Integer, db.ForeignKey('judge.id'))
    player2_id    = db.Column(db.Integer, db.ForeignKey('proposal.id'))
    player1_id    = db.Column(db.Integer, db.ForeignKey('proposal.id'))
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))

    created      = db.Column(db.DateTime, default=func.now())
    last_updated = db.Column(db.DateTime, onupdate=datetime.now)

    def result_for(self, proposal):
        if not self.result: return None
        if proposal == self.player1:
            if self.result == 'player1': return 'victory'
            if self.result == 'tie':     return 'tie'
            return 'defeat'
        elif proposal == self.player2:
            if self.result == 'player2': return 'victory'
            if self.result == 'tie':     return 'tie'
            return 'defeat'
        return None


class Tournament(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    current_round = db.Column(db.Integer, default = 0)
    name          = db.Column(db.Text)
    selection     = db.Column(db.Text, default="*")
    status        = db.Column(db.Enum("open", "closed", name="tournament_statuses"))

    judges  = db.relationship("Judge", backref="tournament", lazy='dynamic')
    matches = db.relationship("Match", backref="tournament", lazy="dynamic")

    @property
    def proposals(self):
        proposals = Proposal.query
        if self.selection != "*":
            proposals = proposals.filter(Proposal.tags.any(ProposalTag.name == self.selection))
        return proposals.all()

    def status_of_round(self, round_number):
        expired_max_time = datetime.now() - timedelta(minutes=15)
        matches = self.matches.filter(Match.round == round_number)

        return dict(
            judged      = matches.filter(Match.result.isnot(None)).count(),
            in_progress = matches.filter(Match.result.is_(None), Match.judge_id.isnot(None)).count(),
            pending     = matches.filter(Match.result.is_(None), Match.judge_id.is_(None)).count(),
            stale       = matches.filter(Match.result.is_(None), Match.judge_id.isnot(None), Match.last_updated <= expired_max_time).count()
        )
