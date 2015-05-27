from contextlib import contextmanager

import json
import mockito

from segue.errors import NotAuthorized

from ..support import SegueApiTestCase, Context
from ..support.factories import *

class JudgeControllerFunctionalTestCases(SegueApiTestCase):
    def setUp(self):
        super(JudgeControllerFunctionalTestCases, self).setUp()

    def setUpData(self):
        tournament = self.create_from_factory(ValidTournamentFactory)

        judge0 = self.create_from_factory(ValidJudgeFactory, id=111, hash="ABCD", votes=5, tournament=tournament)

        acc0 = self.create_from_factory(ValidAccountFactory, name="Jaqen H'ghar", resume="a man has no past")
        acc1 = self.create_from_factory(ValidAccountFactory, name="Arya Stark",   resume="a girl has no past")
        acc2 = self.create_from_factory(ValidAccountFactory, name="Jon Snow",     resume="knows nothing")

        proposal1 = self.create_from_factory(ValidProposalFactory, owner=acc0, title='valar morghulis')
        proposal2 = self.create_from_factory(ValidProposalFactory, owner=acc0, title='valar dohaeris')
        proposal3 = self.create_from_factory(ValidProposalFactory, owner=acc0, title='valar lavarlouca')
        proposal4 = self.create_from_factory(ValidProposalFactory, owner=acc0, title='a man must die')

        coauthor0 = self.create_from_factory(ValidInviteFactory, status="accepted", proposal=proposal1, recipient=acc1.email)
        coauthor1 = self.create_from_factory(ValidInviteFactory, status="accepted", proposal=proposal1, recipient=acc2.email)

        match0 = self.create_from_factory(ValidMatchFactory, tournament=tournament, player1 = proposal1, player2 = proposal2, judge=judge0)
        match1 = self.create_from_factory(ValidMatchFactory, tournament=tournament, player1 = proposal3, player2 = proposal4, judge=None)

        return Context(locals())

    def test_judge_status(self):
        ctx = self.setUpData()

        response = self.jget("/judges/ABCD")
        item = json.loads(response.data)['resource']

        self.assertEquals(response.status_code, 200)
        self.assertEquals(item["hash"], "ABCD")
        self.assertEquals(item["votes"], 5)
        self.assertEquals(item["spent"], 0)
        self.assertEquals(item["remaining"], 5)

    def test_get_match_for_judge(self):
        ctx = self.setUpData()

        response = self.jget("/judges/ABCD/match")
        item = json.loads(response.data)['resource']

        self.assertEquals(response.status_code, 200)
        self.assertEquals(item["id"], ctx.match0.id)
        self.assertEquals(item["player1"]["title"], "valar morghulis")
        self.assertEquals(item["player2"]["title"], "valar dohaeris")

        self.assertEquals(len(item["player1"]["authors"]), 3)
        self.assertEquals(item["player1"]["authors"][0]["name"],   "Jaqen H'ghar")
        self.assertEquals(item["player1"]["authors"][0]["resume"], "a man has no past")

        self.assertEquals(item["player1"]["authors"][1]["name"],   "Arya Stark")
        self.assertEquals(item["player1"]["authors"][1]["resume"], "a girl has no past")

        self.assertEquals(item["player1"]["authors"][2]["name"],   "Jon Snow")
        self.assertEquals(item["player1"]["authors"][2]["resume"], "knows nothing")

        self.assertEquals(len(item["player2"]["authors"]), 1)
        self.assertEquals(item["player2"]["authors"][0], item["player2"]["authors"][0])

    def test_voting_flow_for_a_given_judge(self):
        ctx = self.setUpData()
        raw_vote = json.dumps({ "hash": "ABCD", "vote": "player1" })

        response = self.jget("/judges/ABCD/match")
        match = json.loads(response.data)['resource']

        response = self.jpost("/matches/%d/vote" % match['id'], data=raw_vote)
        self.assertEquals(response.status_code, 200)

        response = self.jpost("/matches/%d/vote" % match['id'], data=raw_vote)
        self.assertEquals(response.status_code, 400)

        response = self.jget("/judges/ABCD")
        judge = json.loads(response.data)['resource']
        self.assertEquals(judge['votes'], 5)
        self.assertEquals(judge['spent'], 1)
        self.assertEquals(judge['remaining'], 4)

        response = self.jget("/judges/ABCD/match")
        match = json.loads(response.data)['resource']

        self.assertNotEqual(match['id'], ctx.match0.id)

