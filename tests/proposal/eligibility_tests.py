import sys

import json
import mockito

from datetime import timedelta, datetime
from freezegun import freeze_time

from segue.proposal.services import ProposalService, InviteService

from ..support import SegueApiTestCase, Context
from ..support.factories import *

class ProponentNonSelectionTestCases(SegueApiTestCase):
    def setUp(self):
        super(ProponentNonSelectionTestCases, self).setUp()

    def setUpScenario(self):
        today     = datetime.now()
        tomorrow  = today + timedelta(days=+1)
        yesterday = today + timedelta(days=-1)

        product = self.create(ValidProponentProductFactory, original_deadline=today)
        acc = self.create(ValidAccountFactory)
        return Context(locals())

    def _propose(self, creation, tags='', coauthors=list(), **kw):
        proposal = self.create(ValidProposalWithOwnerFactory, created=creation, **kw)
        for tag in tags.split(','):
            self.create(ValidProposalTagFactory, name=tag, proposal=proposal)
        for coauthor in coauthors:
            self.create(ValidInviteFactory, proposal=proposal, recipient=coauthor.email, status='accepted')
        return proposal

    def test_confirmed_cases_are_not_eligible(self):
        ctx = self.setUpScenario()
        prop = self._propose(ctx.yesterday, status='confirmed', coauthors=[ctx.acc], tags='player')

        result = ctx.product.check_eligibility({}, prop.owner)
        self.assertEquals(result, False)

        result = ctx.product.check_eligibility({}, ctx.acc)
        self.assertEquals(result, False)

    def test_rejected_only_cases_are_not_eligible(self):
        ctx = self.setUpScenario()
        prop = self._propose(ctx.yesterday, tags='rejected', coauthors=[ctx.acc])

        result = ctx.product.check_eligibility({}, prop.owner)
        self.assertEquals(result, False)

        result = ctx.product.check_eligibility({}, prop.owner)
        self.assertEquals(result, False)

    def test_mixed_rejected_non_accepted_cases_are_eligible(self):
        ctx = self.setUpScenario()
        prop1 = self._propose(ctx.yesterday, coauthors=[ctx.acc], tags='rejected')
        prop2 = self._propose(ctx.yesterday, coauthors=[ctx.acc], owner=prop1.owner,  tags='player')

        result = ctx.product.check_eligibility({}, prop1.owner)
        self.assertEquals(result, True)

        result = ctx.product.check_eligibility({}, ctx.acc)
        self.assertEquals(result, True)

    def test_mixed_confirmed_non_accepted_cases_are_not_eligible(self):
        ctx = self.setUpScenario()
        prop1 = self._propose(ctx.yesterday, status='confirmed', coauthors=[ctx.acc], tags='player')
        prop2 = self._propose(ctx.yesterday, owner=prop1.owner,  coauthors=[ctx.acc], tags='player')

        result = ctx.product.check_eligibility({}, prop1.owner)
        self.assertEquals(result, False)

        result = ctx.product.check_eligibility({}, ctx.acc)
        self.assertEquals(result, False)

    def test_late_only_cases_are_not_eligible(self):
        ctx = self.setUpScenario()
        prop = self._propose(ctx.tomorrow, tags='player', coauthors=[ctx.acc])

        result = ctx.product.check_eligibility({}, prop.owner)
        self.assertEquals(result, False)

        result = ctx.product.check_eligibility({}, ctx.acc)
        self.assertEquals(result, False)

    def test_mixed_early_and_late_cases_are_eligible(self):
        ctx = self.setUpScenario()
        prop1 = self._propose(ctx.yesterday, tags='player', coauthors=[ctx.acc])
        prop2 = self._propose(ctx.tomorrow,  tags='player', coauthors=[ctx.acc], owner=prop1.owner)

        result = ctx.product.check_eligibility({}, prop1.owner)
        self.assertEquals(result, True)

        result = ctx.product.check_eligibility({}, ctx.acc)
        self.assertEquals(result, True)

    def test_valid_cases_are_eligible(self):
        ctx = self.setUpScenario()
        prop = self._propose(ctx.yesterday, tags='player', coauthors=[ctx.acc])

        result = ctx.product.check_eligibility({}, prop.owner)
        self.assertEquals(result, True)

        result = ctx.product.check_eligibility({}, ctx.acc)
        self.assertEquals(result, True)


