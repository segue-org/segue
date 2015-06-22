from flask.ext.jwt import current_user

from segue.core import cache
from segue.decorators import jsoned, jwt_only, admin_only

from segue.judge.services import TournamentService, RankingService

from ..responses import TournamentDetailResponse, TournamentShortResponse, StandingsResponse, RankingResponse

class AdminJudgeController(object):
    def __init__(self, tournaments=None, rankings=None):
        self.current_user = current_user
        self.tournaments = tournaments or TournamentService()
        self.rankings    = rankings or RankingService()

    @jwt_only
    @admin_only
    @jsoned
    def list_tournaments(self):
        result = self.tournaments.all()
        return TournamentShortResponse.create(result), 200

    @jwt_only
    @admin_only
    @jsoned
    def get_tournament(self, tournament_id):
        result = self.tournaments.get_one(tournament_id)
        return TournamentDetailResponse.create(result), 200

    @jwt_only
    @admin_only
    @jsoned
    @cache.cached(timeout=60 * 60)
    def get_standings(self, tournament_id):
        result = self.tournaments.get_standings(tournament_id)
        return StandingsResponse.create(result), 200

    @jwt_only
    @admin_only
    @jsoned
    def get_ranking_by_track(self, tournament_id, track_id):
        result = self.rankings.classificate(tournament_id, track_id=track_id)
        return RankingResponse.create(result), 200


