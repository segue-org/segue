from sqlalchemy import or_, and_
from segue.filters import FilterStrategies

from models import Proposal, ProposalInvite
from ..account.models import Account

class ProposalFilterStrategies(FilterStrategies):
    def enforce_user(self, user):
        return or_(self.by_owner_id(user.id), self.by_coauthor_id(user.id))

    def by_proposal_id(self, value, as_user=None):
        if isinstance(value, basestring) and not value.isdigit(): return
        return Proposal.id == value

    def by_owner_id(self, value, as_user=None):
        if isinstance(value, basestring) and not value.isdigit(): return
        return Proposal.owner_id == value

    def by_coauthor_id(self, value, as_user=None):
        if isinstance(value, basestring) and not value.isdigit(): return
        return Proposal.invites.any(and_(ProposalInvite.recipient == Account.email, Account.id == value))

    def by_track_id(self, value, as_user=None):
        if isinstance(value, basestring) and not value.isdigit(): return
        return Proposal.track_id == value

    def by_title(self, value, as_user=None):
        return Proposal.title.ilike('%'+value+'%')

    def by_status(self, value, as_user=None):
        return Proposal.status == value
