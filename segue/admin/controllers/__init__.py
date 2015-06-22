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
import inspect

from segue.decorators import admin_only, jwt_only
from flask.ext.jwt import current_user

from ..responses import *

from .account import AdminAccountController
from .proposal import AdminProposalController
from .judge import AdminJudgeController
from .schedule import AdminScheduleController

class AdminController(object):
    def __init__(self, purchases=None, payments=None, tournaments=None, rankings=None, notifications=None):
        self.purchases = purchases or PurchaseService()
        self.payments = payments or PaymentService()
        self.tournaments = tournaments or TournamentService()
        self.rankings = rankings or RankingService()
        self.notifications = notifications or NotificationService()
        self.current_user = current_user

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
    def list_call_notification_by_status(self, status):
        result = self.notifications.list_by_status('call', status)
        return CallNotificationResponse.create(result), 200

