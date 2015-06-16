import sys;

import json
import mockito

from datetime import timedelta
from freezegun import freeze_time

from segue.proposal import ProposalService, InviteService
from segue.errors import SegueValidationError, NotAuthorized, DeadlineReached

from ..support import SegueApiTestCase
from ..support.factories import *

class ProposalServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(ProposalServiceTestCases, self).setUp()
        self.mock_deadline = mockito.Mock()
        self.service = ProposalService(deadline=self.mock_deadline)
        self.mock_owner = ValidAccountFactory.create()

    def test_cfp_state_open(self):
        mockito.when(self.mock_deadline).is_past().thenReturn(False)
        result = self.service.cfp_state()
        self.assertEquals(result, 'open')

    def test_cfp_state_closed(self):
        mockito.when(self.mock_deadline).is_past().thenReturn(True)
        result = self.service.cfp_state()
        self.assertEquals(result, 'closed')

    def test_invalid_proposal_raises_validation_error(self):
        proposal = InvalidProposalFactory().to_json()

        with self.assertRaises(SegueValidationError):
            self.service.create(proposal, self.mock_owner)

    def test_create_and_retrieve_of_valid_proposal(self):
        proposal = ValidProposalFactory().to_json()

        saved = self.service.create(proposal, self.mock_owner)
        retrieved = self.service.get_one(saved.id)

        self.assertEquals(saved, retrieved)

    def test_cannot_create_nor_modify_proposal_past_deadline(self):
        proposal = ValidProposalFactory().to_json()
        mockito.when(self.mock_deadline).enforce().thenRaise(DeadlineReached)

        with self.assertRaises(DeadlineReached):
            self.service.create(proposal, self.mock_owner)

        existing = self.create_from_factory(ValidProposalFactory)
        with self.assertRaises(DeadlineReached):
            self.service.modify(existing.id, {}, by=existing.owner)

    def test_non_existing_entity_is_none(self):
        retrieved = self.service.get_one(1234)
        self.assertEquals(retrieved, None)

    def test_modify_proposal_valid_owner(self):
        track1 = ValidTrackFactory.create()
        track2 = ValidTrackFactory.create()
        existing = self.create_from_factory(ValidProposalFactory, owner=self.mock_owner)

        new_data = {}
        new_data['title']    = 'ma new title'
        new_data['full']     = 'ma new full'
        new_data['level']    = 'beginner'
        new_data['language'] = 'pt'
        new_data['track_id'] = track2.id
        self.service.modify(existing.id, new_data, by=self.mock_owner)

        retrieved = self.service.get_one(existing.id)
        self.assertEquals(retrieved.title,    'ma new title')
        self.assertEquals(retrieved.full,     'ma new full')
        self.assertEquals(retrieved.level,    'beginner')
        self.assertEquals(retrieved.language, 'pt')
        self.assertEquals(retrieved.track.id, track2.id)

        # changing owner is a special case, and can't be done by mass update
        self.assertEquals(retrieved.owner, existing.owner)
        # id should never change
        self.assertEquals(retrieved.id,    existing.id)

    def test_change_track_of_proposal(self):
        old_track = self.create_from_factory(ValidTrackFactory)
        new_track = self.create_from_factory(ValidTrackFactory)
        proposal = self.create_from_factory(ValidProposalFactory, track=old_track)

        result    = self.service.change_track(proposal.id, new_track.id)
        retrieved = self.service.get_one(proposal.id)

        self.assertEquals(result, retrieved)
        self.assertEquals(retrieved.track, new_track)


    def test_modify_proposal_wrong_owner(self):
        other_owner = ValidAccountFactory.create()
        existing = self.create_from_factory(ValidProposalFactory, owner=self.mock_owner)

        with self.assertRaises(NotAuthorized):
            new_data = { 'title': 'ma new title' }
            self.service.modify(existing.id, new_data, by=other_owner)

        retrieved = self.service.get_one(existing.id)
        self.assertNotEquals(retrieved.title, 'ma new title')

    def test_list_tracks(self):
        track1 = ValidTrackFactory.create()
        track2 = ValidTrackFactory.create()

        result = self.service.list_tracks()

        self.assertEquals(len(result), 2)
        self.assertEquals(result[0].name_en, track1.name_en)
        self.assertEquals(result[1].name_en, track2.name_en)

    def test_query_proposals_with_auth_check(self):
        owner = self.create_from_factory(ValidAccountFactory)
        proposal1 = self.create_from_factory(ValidProposalFactory, owner=owner)
        proposal2 = self.create_from_factory(ValidProposalWithOwnerFactory)

        result = self.service.query(as_user=owner)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].id, proposal1.id)

    def test_query_proposals_by_owner_with_auth_check(self):
        owner = self.create_from_factory(ValidAccountFactory)
        proposal1 = self.create_from_factory(ValidProposalFactory, owner=owner)
        proposal2 = self.create_from_factory(ValidProposalWithOwnerFactory)

        result = self.service.query(owner_id = owner.id, as_user=owner)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].id, proposal1.id)

        result = self.service.query(owner_id = owner.id, as_user=proposal2.owner)
        self.assertEquals(len(result), 0)

    def test_query_proposals_by_coauthor(self):
        account1 = self.create_from_factory(ValidAccountFactory)

        proposal1 = self.create_from_factory(ValidProposalFactory)
        proposal2 = self.create_from_factory(ValidProposalFactory)
        proposal3 = self.create_from_factory(ValidProposalFactory)

        invite1 = self.create_from_factory(ValidInviteFactory, proposal=proposal1, recipient=account1.email)
        invite2 = self.create_from_factory(ValidInviteFactory, proposal=proposal2)

        result = self.service.query(coauthor_id = account1.id)

        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].id, proposal1.id)

    def test_tag_proposal(self):
        created = self.create_from_factory(ValidProposalFactory)
        self.assertEquals(created.tagged_as('le-tag'), False)

        self.service.tag_proposal(created.id, "le-tag")
        retrieved = self.service.get_one(created.id)

        self.assertEquals(retrieved.tag_names, ["le-tag"])
        self.assertEquals(retrieved.tagged_as('le-tag'), True)

        self.service.tag_proposal(created.id, "autre-tag")
        self.assertEquals(retrieved.tag_names, ["le-tag", "autre-tag"])
        self.assertEquals(retrieved.tagged_as('autre-tag'), True)

        self.service.tag_proposal(created.id, "autre-tag")
        self.assertEquals(retrieved.tag_names, ["le-tag", "autre-tag"])

class InviteServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(InviteServiceTestCases, self).setUp()
        self.mock_hasher = mockito.Mock()
        self.mock_mailer = mockito.Mock()
        self.mock_owner = ValidAccountFactory.create()
        self.mock_deadline = mockito.Mock()
        self.service = InviteService(hasher=self.mock_hasher,
                                     mailer=self.mock_mailer,
                                     deadline=self.mock_deadline)
        self.proposal = self.create_from_factory(ValidProposalFactory, owner=self.mock_owner)

    def test_list_valid_owner(self):
        proposal = self.create_from_factory(ValidProposalFactory, owner=self.mock_owner)
        result = self.service.list(proposal.id, by=self.mock_owner)
        self.assertEquals(result, [])

    def test_list_wrong_owner(self):
        other_owner = ValidAccountFactory.create()
        proposal = self.create_from_factory(ValidProposalFactory, owner=self.mock_owner)

        with self.assertRaises(NotAuthorized):
            self.service.list(proposal.id, by=other_owner)

    def test_invite_coauthor(self):
        invite_data = { 'recipient': 'fulano@example.com', 'name': 'Fulano' }
        mockito.when(self.mock_hasher).generate().thenReturn('123ABC')
        mockito.when(self.mock_mailer).proposal_invite(mockito.any())

        invite = self.service.create(self.proposal.id, invite_data, by=self.mock_owner)

        self.assertEquals(invite.hash,      '123ABC')
        self.assertEquals(invite.recipient, invite_data['recipient'])
        self.assertEquals(invite.name,      invite_data['name'])

        mockito.verify(self.mock_mailer).proposal_invite(invite)

    def test_answer_new_user(self):
        invite = self.create_from_factory(ValidInviteFactory)

        result = self.service.answer(invite.hash, accepted=True)
        retrieved = self.service.get_by_hash(invite.hash)
        self.assertEquals(retrieved.status, 'accepted')

        result = self.service.answer(invite.hash, accepted=False)
        retrieved = self.service.get_by_hash(invite.hash)
        self.assertEquals(retrieved.status, 'declined')

    def test_answer_existing_user(self):
        existing = self.create_from_factory(ValidAccountFactory)
        other_user = self.create_from_factory(ValidAccountFactory)
        invite = self.create_from_factory(ValidInviteFactory, recipient=existing.email)

        with self.assertRaises(NotAuthorized):
            result = self.service.answer(invite.hash, accepted=True, by=None)

        with self.assertRaises(NotAuthorized):
            result = self.service.answer(invite.hash, accepted=True, by=other_user)

        result = self.service.answer(invite.hash, accepted=True, by=existing)
        retrieved = self.service.get_by_hash(invite.hash)
        self.assertEquals(retrieved.status, 'accepted')

    def test_register_from_invite(self):
        mock_accounts = self.service.accounts = mockito.Mock()
        invite = self.create_from_factory(ValidInviteFactory)
        fake_account = mockito.Mock()
        fake_data = dict(email=invite.recipient)
        mockito.when(mock_accounts).create(fake_data).thenReturn(fake_account)

        result = self.service.register(invite.hash, fake_data)
        mockito.verify(mock_accounts).create(fake_data)
        self.assertEquals(result, fake_account)

        with self.assertRaises(NotAuthorized):
            self.service.register(invite.hash, dict(email='other@email.com'))

    def test_cannot_invite_nor_answer_invite_nor_register_past_deadline(self):
        mockito.when(self.mock_deadline).enforce().thenRaise(DeadlineReached)

        with self.assertRaises(DeadlineReached):
            self.service.create(self.proposal.id, {}, by=self.mock_owner)

        with self.assertRaises(DeadlineReached):
            self.service.answer('ANY', accepted=True)

        with self.assertRaises(DeadlineReached):
            self.service.register('ANY', {})


