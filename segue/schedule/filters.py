from datetime import date, datetime

from segue.proposal.models import Proposal
from segue.account.models import Account
from segue.filters import FilterStrategies

from models import Slot, Room

class SlotFilterStrategies(FilterStrategies):
    def by_room(self, value, as_user=None):
        if isinstance(value, Room):
            return Slot.room == value
        else:
            return Slot.room_id == value

    def by_day(self, value, as_user=None):
        if isinstance(value, date):
            value = datetime(value.year, value.month, value.day)
        if isinstance(value, basestring):
            try:
                value = datetime.strptime(value,"%Y-%m-%d")
            except ValueError, e:
                value = None
        if not isinstance(value, datetime):
            return None
        day_start = value.replace(hour=0,  minute=0,  second=0)
        day_end   = value.replace(hour=23, minute=59, second=59)
        return Slot.begins.between(day_start, day_end)

    def by_blocked(self, value, as_user=None):
        return Slot.blocked == value

    def by_status(self, value, as_user=None):
        return Slot.status == value

    def by_available(self, value, as_user=None):
        if value:
            return Slot.talk == None
        return Slot.talk != None

    def by_title(self, value, as_user=None):
        return Proposal.title.ilike('%'+value+'%')

    def by_speaker(self, value, as_user=None):
        return Account.name.ilike('%'+value+'%')

    def join_for_title(self, queryset, needle=None):
        return queryset.join(Proposal)

    def join_for_speaker(self, queryset, needle=None):
        return queryset.join(Proposal).join(Account)
