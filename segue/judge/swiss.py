from models import Match
from errors import RoundHasPendingMatches

class TrivialRoundGenerator(object):
    def generate(self, players, past_matches, round=1):
        matches = []

        for match in past_matches:
            if match.result == None:
                raise RoundHasPendingMatches()

        for i in range(0, len(players), 2):
            if i + 1 == len(players): # BYE case
                match = Match(player1 = players[i].proposal, round=round, result='player1')
            else:
                match = Match(player1 = players[i].proposal, player2 = players[i+1].proposal, round=round)
            matches.append(match)

        return matches

class ClassicalRoundGenerator(object):
    def _index_past(self, players, past_matches):
        result = { None: {} }
        for p1 in players:
            result[p1.id] = {}
            result[p1.id][None] = False
            for p2 in players:
                result[p1.id][p2.id] = False

        for match in past_matches:
            if match.result == None:
                raise RoundHasPendingMatches()
            result[match.player1_id][match.player2_id] = True
            result[match.player2_id][match.player1_id] = True

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
                if other_idx == len(players): # BYE case
                    print "-- has no one else to pair with, so it gets a freebie"
                    match = Match(player1 = player.proposal, round=round, result='player1')
                    matches.append(match)
                    matched_players.add(player)
                    break;

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
    def __init__(self, proposal, points, victories=0, ties=0, defeats=0):
        self.initial_points = points
        self.id = proposal.id
        self.proposal = proposal
        self.victories = victories
        self.ties = ties
        self.defeats = defeats
        self.position = None

    def add_result(self, result_kind):
        if result_kind == 'victory': self.victories += 1
        if result_kind == 'tie':     self.ties      += 1
        if result_kind == 'defeat':  self.defeats   += 1
        pass

    @property
    def points(self):
        return self.initial_points + self.victories * 3 + self.ties

    def __cmp__(self, other):
        if self.points != other.points:
            return self.points.__cmp__(other.points)
        elif self.victories != other.victories:
            return self.victories.__cmp__(other.victories)
        else:
            return -self.id.__cmp__(other.id)

class StandingsCalculator(object):
   def calculate(self, unordered_proposals, past_matches):
        print 'started pointing...'
        players = {}

        for proposal in unordered_proposals:
            players[proposal.id] = Player(proposal, 0)

        for match in past_matches:
            players[match.player1.id].add_result(match.result_for(match.player1))
            if match.player2:
                players[match.player2.id].add_result(match.result_for(match.player2))
        players = players.values()

        print 'started sorting'
        players.sort(reverse=True)
        print 'done sorting'

        for idx, player in enumerate(players):
            player.position = idx+1

        return players


