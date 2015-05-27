from segue.core import db
from segue.errors import MatchAlreadyJudged, MatchAssignedToOtherJudge, InvalidJudge, NoMatchAvailable
from models import Judge, Match, Tournament


class TrivialRoundGenerator(object):
    def generate(self, players, past_matches, round=1):
        matches = []

        for i in range(0, len(players), 2):
            match = Match(player1 = players[i].proposal, player2 = players[i+1].proposal, round=round)
            matches.append(match)

        return matches

class ClassicalRoundGenerator(object):
    def _index_past(self, players, past_matches):
        result = {}
        for p1 in players:
            result[p1.id] = {}
            for p2 in players:
                result[p1.id][p2.id] = False

        for match in past_matches:
            result[match.player1.id][match.player2.id] = True
            result[match.player2.id][match.player1.id] = True
        return result


    def generate(self, players, past_matches, round):
        matches = []

        indexed_past = self._index_past(players, past_matches)
        matched_players = set()

        for idx, player in enumerate(players):
            print "start on idx={}, pid={}".format(idx, player.id)
            if player in matched_players:
                print "-- {} already matched for this round...".format(player.id)
                continue

            other_idx = idx
            while True:
                other_idx += 1
                other_player = players[other_idx]
                print "-- trying to pair {} with {}...".format(player.id, other_player.id)
                if other_player in matched_players:
                    print "---- nope, p2 is alread matched for this round"
                    continue

                if indexed_past[player.id][other_player.id]:
                    print "---- {} and {} already played before...".format(player.id, other_player.id)
                    continue

                print "---- pairing is good, creating match!"
                match = Match(player1=player.proposal, player2=other_player.proposal, round=round)
                matches.append(match)
                matched_players.add(player)
                matched_players.add(other_player)
                break

        return matches

class Player(object):
    def __init__(self, proposal, points):
        self.points = points
        self.id = proposal.id
        self.proposal = proposal
    def __cmp__(self, other):
        if self.points == other.points:
            return -self.id.__cmp__(other.id)
        return self.points.__cmp__(other.points)

class StandingsCalculator(object):
   def calculate(self, unordered_proposals, past_matches):
        players = []
        for proposal in unordered_proposals:
            points = sum([ match.points_for(proposal) for match in past_matches ])
            players.append(Player(proposal, points))
        players.sort(reverse=True)
        return players

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

class JudgeService(object):
    def __init__(self, db_impl=None):
        self.db = db_impl or db

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
