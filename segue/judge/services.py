from segue.core import db
from segue.hasher import Hasher

from models import Judge, Match, Tournament
from errors import *
from swiss import TrivialRoundGenerator, ClassicalRoundGenerator, StandingsCalculator

class TournamentService(object):
    def __init__(self, db_impl=None, trivial=None, classical=None, standings=None):
        self.db = db_impl or db
        self.trivial = trivial or TrivialRoundGenerator()
        self.classical = classical or ClassicalRoundGenerator()
        self.standings = standings or StandingsCalculator()

    def generate_round(self, tournament_id):
        tournament = Tournament.query.get(tournament_id)
        players = self.standings.calculate(tournament.proposals, tournament.matches)

        if tournament.current_round == 0:
            generator = self.trivial
        else:
            generator = self.classical

        new_matches = generator.generate(players, tournament.matches, tournament.current_round+1)
        for match in new_matches:
            db.session.add(match)
        db.session.commit()

        return new_matches

    def get_one(self, tournament_id):
        tournament = Tournament.query.get(tournament_id)
        if not tournament: raise NoSuchTournament()
        return tournament

class JudgeService(object):
    def __init__(self, db_impl=None, hasher=None, tournaments=None):
        self.db          = db_impl or db
        self.hasher      = hasher or Hasher()
        self.tournaments = tournaments or TournamentService()

    def create_token(self, email, votes, tournament_id):
        tournament = self.tournaments.get_one(tournament_id)
        existing_token = Judge.query.filter(Judge.email == email, Judge.tournament == tournament).first()
        if existing_token: raise JudgeAlreadyExists()

        judge = Judge(email=email, votes=votes)
        judge.hash       = self.hasher.generate()
        judge.tournament = tournament

        db.session.add(judge)
        db.session.commit()
        return judge

    def get_by_hash(self, hash_code):
        judge = Judge.query.filter(Judge.hash == hash_code).first()
        if not judge:
            raise InvalidJudge()
        return judge

    def get_next_match_for(self, hash_code):
        judge = self.get_by_hash(hash_code)
        match = Match.query.filter(Match.judge == judge, Match.result == None).first()
        if not match:
            match = Match.query.filter(Match.result == None).first()
            match.judge = judge
            db.session.add(match)
            db.session.commit()
        return match

    def judge_match(self, match_id, hash_code, result):
        match = Match.query.get(match_id)
        if match.result != None:
            raise MatchAlreadyJudged()
        elif match.judge.hash != hash_code:
            raise MatchAssignedToOtherJudge()
        match.result = result

        db.session.add(match)
        db.session.commit()

        return match
