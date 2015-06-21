from datetime import datetime, timedelta
from segue.core import db
from segue.hasher import Hasher

from models import Judge, Match, Tournament
from errors import *
from swiss import TrivialRoundGenerator, ClassicalRoundGenerator, StandingsCalculator
from segue.proposal.services import ProposalService

class TournamentService(object):
    def __init__(self, db_impl=None, trivial=None, classical=None, standings=None):
        self.db = db_impl or db
        self.trivial = trivial or TrivialRoundGenerator()
        self.classical = classical or ClassicalRoundGenerator()
        self.standings = standings or StandingsCalculator()

    def create_tournament(self, selection="*"):
        tournament = Tournament(selection=selection)
        db.session.add(tournament)
        db.session.commit()
        return tournament

    def get_standings(self, tournament_id):
        tournament = Tournament.query.get(tournament_id)
        return self.standings.calculate(tournament.proposals, tournament.matches)

    def generate_round(self, tournament_id):
        tournament = Tournament.query.get(tournament_id)
        players = self.standings.calculate(tournament.proposals, tournament.matches)

        if tournament.current_round == 0:
            generator = self.trivial
        else:
            generator = self.classical

        new_matches = generator.generate(players, tournament.matches, tournament.current_round+1)
        for match in new_matches:
            match.tournament = tournament
            db.session.add(match)
        tournament.current_round += 1
        db.session.add(tournament)
        db.session.commit()

        return new_matches

    def get_one(self, tournament_id):
        tournament = Tournament.query.get(tournament_id)
        if not tournament: raise NoSuchTournament()
        return tournament

    def all(self):
        return Tournament.query.all()

class Ranked(object):
    def __init__(self, proposal, idx_standings):
        self.proposal = proposal
        self.tag_names = proposal.tag_names
        if proposal.id in idx_standings:
            self.rank = idx_standings[proposal.id].position
        elif "approved" in proposal.tag_names:
            self.rank = 0
        else:
            self.rank = 1000
    def __cmp__(self, other):
        return self.rank.__cmp__(other.rank)

class RankingService(object):
    def __init__(self, tournaments=None, proposals=None):
        self.tournaments = tournaments or TournamentService()
        self.proposals   = proposals   or ProposalService()

    def classificate(self, tournament_id, **filters):
        standings = self.tournaments.get_standings(tournament_id)
        proposals = self.proposals.query(**filters)

        idx_standings = { player.id: player for player in standings }

        unsorted = [ Ranked(proposal, idx_standings) for proposal in proposals ]
        return sorted(unsorted)

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
        if judge.remaining <= 0: raise JudgeHasNoVotesLeft()

        pending_matches = judge.tournament.matches.filter(Match.result == None)
        expired_max_time = datetime.now() - timedelta(minutes=15)

        was_assigned_to_me       = pending_matches.filter(Match.judge == judge).first()
        non_assigned_match       = pending_matches.filter(Match.judge == None).first()
        stale_but_assigned_match = pending_matches.filter(Match.judge != None, Match.last_updated < expired_max_time).first()

        if was_assigned_to_me:
            selected_match = was_assigned_to_me
        elif non_assigned_match:
            selected_match = non_assigned_match
        elif stale_but_assigned_match:
            selected_match = stale_but_assigned_match
        else:
            raise RoundIsOver()

        selected_match.judge = judge
        db.session.add(selected_match)
        db.session.commit()
        return selected_match

    def judge_match(self, match_id, hash_code, vote):
        match = Match.query.get(match_id)
        if match.result != None:
            raise MatchAlreadyJudged()
        elif match.judge.hash != hash_code:
            raise MatchAssignedToOtherJudge()
        match.result = vote

        db.session.add(match)
        db.session.commit()

        return match
