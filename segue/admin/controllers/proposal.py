import flask
from flask import request
from flask.ext.jwt import current_user

from segue.decorators import jsoned, jwt_only, admin_only
from segue.core import logger

from segue.proposal.services import ProposalService

from ..responses import ProposalDetailResponse, ProposalInviteResponse

class AdminProposalController(object):
    def __init__(self, service=None):
        self.service = service or ProposalService()
        self.current_user = current_user

    @jwt_only
    @admin_only
    @jsoned
    def list(self):
        parms = request.args.to_dict()
        result = self.service.lookup(as_user=self.current_user, **parms)
        return ProposalDetailResponse.create(result), 200

    @jwt_only
    @admin_only
    @jsoned
    def list_invites(self, proposal_id=None):
        proposal = self.service.get_one(proposal_id) or abort(404)
        return ProposalInviteResponse.create(proposal.invites.all()), 200

    @jwt_only
    @admin_only
    @jsoned
    def get_one(self, proposal_id=None):
        result = self.service.get_one(proposal_id)
        return ProposalDetailResponse.create(result), 200

    @jwt_only
    @admin_only
    @jsoned
    def change_track(self, proposal_id):
        data = request.get_json()
        old_track_id = self.service.get_one(proposal_id).track_id
        new_track_id = data.get('track_id', None) or flask.abort(400)
        result = self.service.change_track(proposal_id, new_track_id)

        logger.info("user %s changed track of proposal %d. track was %d, now is %d", self.current_user.email, proposal_id, old_track_id, new_track_id)

        return ProposalDetailResponse(result), 200

    @jwt_only
    @admin_only
    @jsoned
    def add_tag(self, proposal_id, tag_name):
        result = self.service.tag_proposal(proposal_id, tag_name)
        logger.info("user %s added tag %s to proposal %d", self.current_user.email, tag_name, proposal_id)
        return ProposalDetailResponse(result), 200

    @jwt_only
    @admin_only
    @jsoned
    def remove_tag(self, proposal_id, tag_name):
        result = self.service.untag_proposal(proposal_id, tag_name)
        logger.info("user %s removed tag %s from proposal %d", self.current_user.email, tag_name, proposal_id)
        return ProposalDetailResponse(result), 200

