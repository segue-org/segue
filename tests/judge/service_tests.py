from datetime import timedelta, datetime
import mockito

from ..support import SegueApiTestCase, Context
from ..support.factories import *

from segue.judge.errors import *
from segue.judge.services import JudgeService, TournamentService


class JudgeTestCases(SegueApiTestCase):
    def setUpProposals(self, ctx=dict()):
        t0 = self.create_from_factory(ValidTournamentFactory, current_round=0, selection="*")
        t1 = self.create_from_factory(ValidTournamentFactory, current_round=1, selection="player")

        p1 = self.create_from_factory(ValidProposalFactory, id=1, title='valar morghulis')
        p2 = self.create_from_factory(ValidProposalFactory, id=2, title='valar dohaeris')
        p3 = self.create_from_factory(ValidProposalFactory, id=3, title='valar lavarlouca')
        p4 = self.create_from_factory(ValidProposalFactory, id=4, title='a man must die')
        p5 = self.create_from_factory(ValidProposalFactory, id=5, title='for the night is dark')
        p6 = self.create_from_factory(ValidProposalFactory, id=6, title='and full of terrors')

        tag0 = self.create_from_factory(ValidProposalTagFactory, name="player", proposal=p1)
        tag1 = self.create_from_factory(ValidProposalTagFactory, name="player", proposal=p2)
        tag2 = self.create_from_factory(ValidProposalTagFactory, name="player", proposal=p3)
        tag3 = self.create_from_factory(ValidProposalTagFactory, name="player", proposal=p4)

        j1 = self.create_from_factory(ValidJudgeFactory, tournament=t0, hash="ABC", votes=5)
        j2 = self.create_from_factory(ValidJudgeFactory, tournament=t0, hash="DEF", votes=5)
        j3 = self.create_from_factory(ValidJudgeFactory, tournament=t0, hash="GHI", votes=5)
        j4 = self.create_from_factory(ValidJudgeFactory, tournament=t0, hash="JKL", votes=5)

        ctx.update(locals())
        return Context(ctx)

    def setUpExistingMatches(self, ctx=dict()):
        m1 = self.create_from_factory(ValidMatchFactory, player1=ctx.p1, player2=ctx.p2, tournament=ctx.t0, result="player1")
        m2 = self.create_from_factory(ValidMatchFactory, player1=ctx.p3, player2=ctx.p4, tournament=ctx.t0, result="tie")
        m3 = self.create_from_factory(ValidMatchFactory, player1=ctx.p5, player2=ctx.p6, tournament=ctx.t0, result="player2")
        ctx.update(locals())
        return Context(ctx)

    def setUpExistingRoundWithPendingMatches(self, ctx=dict()):
        m1 = self.create_from_factory(ValidMatchFactory, player1=ctx.p1, player2=ctx.p2, tournament=ctx.t0, result="player1")
        m2 = self.create_from_factory(ValidMatchFactory, player1=ctx.p3, player2=ctx.p4, tournament=ctx.t0, result=None)
        m3 = self.create_from_factory(ValidMatchFactory, player1=ctx.p5, player2=ctx.p6, tournament=ctx.t0, result=None)
        ctx.update(locals())
        return Context(ctx)

class JudgeServiceTestCases(JudgeTestCases):
    def setUp(self):
        super(JudgeServiceTestCases, self).setUp()
        self.mock_hasher = mockito.Mock()
        self.service = JudgeService(hasher=self.mock_hasher)

    def test_create_tokens(self):
        ctx = self.setUpProposals()
        mockito.when(self.mock_hasher).generate().thenReturn("ABCDEF")

        created = self.service.create_token("fulano@example.com", 5, ctx.t0.id)

        self.assertEquals(created.votes, 5)
        self.assertEquals(created.remaining, 5)
        self.assertEquals(created.spent, 0)
        self.assertEquals(created.email, "fulano@example.com")
        self.assertEquals(created.hash, "ABCDEF")

        retrieved = self.service.get_by_hash("ABCDEF")
        self.assertEquals(created, retrieved)

        with self.assertRaises(JudgeAlreadyExists):
            self.service.create_token("fulano@example.com", 5, ctx.t0.id)

    def test_multiple_judges(self):
        ctx = self.setUpProposals()
        ctx = self.setUpExistingRoundWithPendingMatches(ctx)

        mj1 = self.service.get_next_match_for('ABC')
        mj2 = self.service.get_next_match_for('DEF')

        self.assertEquals(mj1, ctx.m2)
        self.assertEquals(mj2, ctx.m3)

        mj1_again = self.service.get_next_match_for('ABC')
        self.assertEquals(mj1_again, ctx.m2)

        self.service.judge_match(mj1.id, 'ABC', 'tie')

        with self.assertRaises(RoundIsOver):
            self.service.get_next_match_for('JKL')

        with self.assertRaises(RoundIsOver):
            self.service.get_next_match_for('ABC')

class TournamentServiceTestCases(JudgeTestCases):
    def setUp(self):
        super(TournamentServiceTestCases, self).setUp()
        self.mock_trivial   = mockito.Mock()
        self.mock_classical = mockito.Mock()
        self.mock_standings = mockito.Mock()
        self.service   = TournamentService(trivial=self.mock_trivial, classical=self.mock_classical, standings=self.mock_standings)

    def _build_matches(self, *pairs):
        return [ Match(player1=p[0], player2=p[1]) for p in pairs ]

    def test_get_one(self):
        ctx = self.setUpProposals()

        result = self.service.get_one(ctx.t0.id)
        self.assertEquals(result, ctx.t0)

        with self.assertRaises(NoSuchTournament):
            self.service.get_one(567)

    def test_tournament_filters_proposals(self):
        ctx = self.setUpProposals()

        self.assertEquals(len(ctx.t0.proposals), 6)
        self.assertEquals(len(ctx.t1.proposals), 4)
        self.assertEquals(ctx.t1.proposals[0], ctx.p1)
        self.assertEquals(ctx.t1.proposals[1], ctx.p2)
        self.assertEquals(ctx.t1.proposals[2], ctx.p3)
        self.assertEquals(ctx.t1.proposals[3], ctx.p4)

    def test_uses_trivial_round_generator_on_round_zero(self):
        ctx = self.setUpProposals()

        ordered_players    = [ctx.p1,ctx.p2,ctx.p3,ctx.p4,ctx.p5,ctx.p6]
        shuffled_proposals = [ctx.p5,ctx.p3,ctx.p1,ctx.p1,ctx.p2,ctx.p4]

        fake_matches = self._build_matches([ctx.p1, ctx.p2], [ctx.p3, ctx.p4], [ctx.p5, ctx.p6])

        mockito.when(self.mock_standings).calculate(mockito.any(), mockito.any()).thenReturn(ordered_players)
        mockito.when(self.mock_trivial).generate(ordered_players, mockito.any(), 1).thenReturn(fake_matches)

        new_matches = self.service.generate_round(ctx.t0.id)

        self.assertEquals(new_matches, fake_matches)
        self.assertIsNotNone(new_matches[0].id)
        self.assertIsNotNone(new_matches[1].id)
        self.assertIsNotNone(new_matches[2].id)
        self.assertEquals(new_matches[0].tournament, ctx.t0)
        self.assertEquals(new_matches[1].tournament, ctx.t0)
        self.assertEquals(new_matches[2].tournament, ctx.t0)

    def test_uses_classical_round_generator_on_other_rounds(self):
        ctx = self.setUpProposals()

        ordered_players    = [ctx.p1,ctx.p2,ctx.p3,ctx.p4,ctx.p5,ctx.p6]
        shuffled_proposals = [ctx.p5,ctx.p3,ctx.p1,ctx.p1,ctx.p2,ctx.p4]

        fake_matches = self._build_matches([ctx.p1, ctx.p3], [ctx.p2, ctx.p5], [ctx.p4, ctx.p6])

        mockito.when(self.mock_standings).calculate(mockito.any(), mockito.any()).thenReturn(ordered_players)
        mockito.when(self.mock_classical).generate(ordered_players, mockito.any(), 2).thenReturn(fake_matches)

        new_matches = self.service.generate_round(ctx.t1.id)

        self.assertEquals(new_matches, fake_matches)
        self.assertIsNotNone(new_matches[0].id)
        self.assertIsNotNone(new_matches[1].id)
        self.assertIsNotNone(new_matches[2].id)
        self.assertEquals(new_matches[0].tournament, ctx.t1)
        self.assertEquals(new_matches[1].tournament, ctx.t1)
        self.assertEquals(new_matches[2].tournament, ctx.t1)


