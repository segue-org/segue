from datetime import timedelta, datetime
import mockito

from segue.judge.services import TournamentService, StandingsCalculator, TrivialRoundGenerator, Player, ClassicalRoundGenerator
from ..support import SegueApiTestCase, Context
from ..support.factories import *


class JudgeTestCases(SegueApiTestCase):
    def setUpProposals(self, ctx=dict()):
        tournament0 = self.create_from_factory(ValidTournamentFactory, current_round=0)
        tournament1 = self.create_from_factory(ValidTournamentFactory, current_round=1)

        p1 = self.create_from_factory(ValidProposalFactory, id=1, title='valar morghulis')
        p2 = self.create_from_factory(ValidProposalFactory, id=2, title='valar dohaeris')
        p3 = self.create_from_factory(ValidProposalFactory, id=3, title='valar lavarlouca')
        p4 = self.create_from_factory(ValidProposalFactory, id=4, title='a man must die')
        p5 = self.create_from_factory(ValidProposalFactory, id=5, title='for the night is dark')
        p6 = self.create_from_factory(ValidProposalFactory, id=6, title='and full of terrors')
        ctx.update(locals())
        return Context(ctx)

    def setUpExistingMatches(self, ctx=dict()):
        m1 = self.create_from_factory(ValidMatchFactory, player1=ctx.p1, player2=ctx.p2, result="player1")
        m2 = self.create_from_factory(ValidMatchFactory, player1=ctx.p3, player2=ctx.p4, result="tie")
        m3 = self.create_from_factory(ValidMatchFactory, player1=ctx.p5, player2=ctx.p6, result="player2")
        ctx.update(locals())
        return Context(ctx)

class TournamentServiceTestCases(JudgeTestCases):
    def setUp(self):
        super(TournamentServiceTestCases, self).setUp()
        self.mock_trivial   = mockito.Mock()
        self.mock_classical = mockito.Mock()
        self.mock_standings = mockito.Mock()
        self.service   = TournamentService(trivial=self.mock_trivial, classical=self.mock_classical, standings=self.mock_standings)

    def _build_matches(self, *pairs):
        return [ Match(player1=p[0], player2=p[1]) for p in pairs ]

    def test_uses_trivial_round_generator_on_round_zero(self):
        ctx = self.setUpProposals()

        ordered_players    = [ctx.p1,ctx.p2,ctx.p3,ctx.p4,ctx.p5,ctx.p6]
        shuffled_proposals = [ctx.p5,ctx.p3,ctx.p1,ctx.p1,ctx.p2,ctx.p4]

        fake_matches = self._build_matches([ctx.p1, ctx.p2], [ctx.p3, ctx.p4], [ctx.p5, ctx.p6])

        mockito.when(self.mock_standings).calculate(mockito.any(), mockito.any()).thenReturn(ordered_players)
        mockito.when(self.mock_trivial).generate(ordered_players, mockito.any(), 1).thenReturn(fake_matches)

        new_matches = self.service.generate_round(ctx.tournament0.id)

        self.assertEquals(new_matches, fake_matches)
        self.assertIsNotNone(new_matches[0].id)
        self.assertIsNotNone(new_matches[1].id)
        self.assertIsNotNone(new_matches[2].id)

    def test_uses_classical_round_generator_on_other_rounds(self):
        ctx = self.setUpProposals()

        ordered_players    = [ctx.p1,ctx.p2,ctx.p3,ctx.p4,ctx.p5,ctx.p6]
        shuffled_proposals = [ctx.p5,ctx.p3,ctx.p1,ctx.p1,ctx.p2,ctx.p4]

        fake_matches = self._build_matches([ctx.p1, ctx.p3], [ctx.p2, ctx.p5], [ctx.p4, ctx.p6])

        mockito.when(self.mock_standings).calculate(mockito.any(), mockito.any()).thenReturn(ordered_players)
        mockito.when(self.mock_classical).generate(ordered_players, mockito.any(), 2).thenReturn(fake_matches)

        new_matches = self.service.generate_round(ctx.tournament1.id)

        self.assertEquals(new_matches, fake_matches)
        self.assertIsNotNone(new_matches[0].id)
        self.assertIsNotNone(new_matches[1].id)
        self.assertIsNotNone(new_matches[2].id)

class TrivialRoundGeneratorTestCases(JudgeTestCases):
    def setUp(self):
        super(TrivialRoundGeneratorTestCases, self).setUp()
        self.generator = TrivialRoundGenerator()

    def test_pairs_players_two_by_two(self):
        ctx = self.setUpProposals()

        ordered_players  = [ Player(p,0) for p in [ctx.p1,ctx.p2,ctx.p3,ctx.p4,ctx.p5,ctx.p6]]
        past_matches = []

        result = self.generator.generate(ordered_players, past_matches, round=1)

        self.assertEquals(len(result), 3)
        self.assertEquals([ x.round for x in result ], [1,1,1])
        self.assertEquals(result[0].player1, ctx.p1)
        self.assertEquals(result[0].player2, ctx.p2)
        self.assertEquals(result[1].player1, ctx.p3)
        self.assertEquals(result[1].player2, ctx.p4)
        self.assertEquals(result[2].player1, ctx.p5)
        self.assertEquals(result[2].player2, ctx.p6)

class ClassicalRoundGeneratorTestCases(JudgeTestCases):
    def setUp(self):
        super(ClassicalRoundGeneratorTestCases, self).setUp()
        self.generator = ClassicalRoundGenerator()

    def test_does_not_repeat_already_existing_match(self):
        ctx = self.setUpProposals()
        ctx = self.setUpExistingMatches(ctx)

        ordered_players  = [ Player(p,0) for p in [ctx.p1,ctx.p6,ctx.p3,ctx.p4,ctx.p2,ctx.p5]]
        past_matches = [ctx.m1,ctx.m2,ctx.m3]

        result = self.generator.generate(ordered_players, past_matches, 2)
        self.assertEquals(result[0].player1, ctx.p1)
        self.assertEquals(result[0].player2, ctx.p6)
        self.assertEquals(result[1].player1, ctx.p3)
        self.assertEquals(result[1].player2, ctx.p2)
        self.assertEquals(result[2].player1, ctx.p4)
        self.assertEquals(result[2].player2, ctx.p5)


class StandingsCalculatorTestCases(JudgeTestCases):
    def setUp(self):
        super(StandingsCalculatorTestCases, self).setUp()
        self.calculator = StandingsCalculator()

    def test_defaults_to_proposal_id(self):
        ctx = self.setUpProposals()

        shuffled_proposals = [ctx.p5,ctx.p3,ctx.p1,ctx.p6,ctx.p2,ctx.p4]
        past_matches = []

        result = self.calculator.calculate(shuffled_proposals, past_matches)

        self.assertEquals(result[0].proposal, ctx.p1)
        self.assertEquals(result[1].proposal, ctx.p2)
        self.assertEquals(result[2].proposal, ctx.p3)
        self.assertEquals(result[3].proposal, ctx.p4)
        self.assertEquals(result[4].proposal, ctx.p5)
        self.assertEquals(result[5].proposal, ctx.p6)

    def test_sorts_by_number_of_points(self):
        ctx = self.setUpProposals()
        ctx = self.setUpExistingMatches(ctx)

        shuffled_proposals = [ctx.p5,ctx.p3,ctx.p1,ctx.p6,ctx.p2,ctx.p4]
        past_matches = [ctx.m1,ctx.m2,ctx.m3]

        result = self.calculator.calculate(shuffled_proposals, past_matches)

        self.assertEquals(result[0].proposal, ctx.p1) # won 1, has lowest id
        self.assertEquals(result[1].proposal, ctx.p6) # won 1, higher id
        self.assertEquals(result[2].proposal, ctx.p3) # tied 1, lower id
        self.assertEquals(result[3].proposal, ctx.p4) # tied 1, higher id
        self.assertEquals(result[4].proposal, ctx.p2) # lost 1, lower id
        self.assertEquals(result[5].proposal, ctx.p5) # lost 1, higher id
