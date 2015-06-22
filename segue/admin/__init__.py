from functools import wraps

from flask import request, url_for, abort
from flask.ext.jwt import current_user

from segue.errors import NotAuthorized
from segue.core import config, logger, cache
from segue.json import SimpleJson
from segue.decorators import jsoned, admin_only, jwt_only

from segue.account.services import AccountService
from segue.proposal.services import ProposalService
from segue.purchase.services import PurchaseService, PaymentService
from segue.judge.services import TournamentService, RankingService
from segue.schedule.services import NotificationService

from responses import *


class AdminController(object):
    def __init__(self, proposals=None, purchases=None, payments=None, tournaments=None, rankings=None, notifications=None):
        self.proposals = proposals or ProposalService()
        self.purchases = purchases or PurchaseService()
        self.payments = payments or PaymentService()
        self.tournaments = tournaments or TournamentService()
        self.rankings = rankings or RankingService()
        self.notifications = notifications or NotificationService()
        self.current_user = current_user

    @jwt_only
    @admin_only
    @jsoned
    def list_proposals(self):
        parms = request.args.to_dict()
        result = self.proposals.lookup(as_user=self.current_user, **parms)
        return ProposalDetailResponse.create(result), 200

    @jwt_only
    @admin_only
    @jsoned
    def list_proposal_invites(self, proposal_id=None):
        proposal = self.proposals.get_one(proposal_id) or abort(404)
        return ProposalInviteResponse.create(proposal.invites.all()), 200

    @jwt_only
    @admin_only
    @jsoned
    def get_proposal(self, proposal_id=None):
        result = self.proposals.get_one(proposal_id)
        return ProposalDetailResponse.create(result), 200

    @jwt_only
    @admin_only
    @jsoned
    def list_purchases(self):
        parms = request.args.to_dict()
        result = self.purchases.query(as_user=self.current_user, **parms)
        return PurchaseDetailResponse.create(result), 200

    @jwt_only
    @admin_only
    @jsoned
    def list_caravans(self):
        return [], 200

    @jwt_only
    @admin_only
    @jsoned
    def list_payments(self):
        parms = request.args.to_dict()
        result = self.payments.query(as_user=self.current_user, **parms)
        return PaymentDetailResponse.create(result), 200

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

    @jwt_only
    @admin_only
    @jsoned
    def change_track_of_proposal(self, proposal_id):
        data = request.get_json()
        old_track_id = self.proposals.get_one(proposal_id).track_id
        new_track_id = data.get('track_id', None) or flask.abort(400)
        result = self.proposals.change_track(proposal_id, new_track_id)

        logger.info("user %s changed track of proposal %d. track was %d, now is %d", self.current_user.email, proposal_id, old_track_id, new_track_id)

        return ProposalDetailResponse(result), 200

    @jwt_only
    @admin_only
    @jsoned
    def list_call_notification_by_status(self, status):
        result = self.notifications.list_by_status('call', status)
        return CallNotificationResponse.create(result), 200

    @jwt_only
    @admin_only
    @jsoned
    def add_tag_to_proposal(self, proposal_id, tag_name):
        result = self.proposals.tag_proposal(proposal_id, tag_name)
        logger.info("user %s added tag %s to proposal %d", self.current_user.email, tag_name, proposal_id)
        return ProposalDetailResponse(result), 200

    @jwt_only
    @admin_only
    @jsoned
    def remove_tag_from_proposal(self, proposal_id, tag_name):
        result = self.proposals.untag_proposal(proposal_id, tag_name)
        logger.info("user %s removed tag %s from proposal %d", self.current_user.email, tag_name, proposal_id)
        return ProposalDetailResponse(result), 200

