from datetime import datetime

from segue.core import db
from segue.mailer import MailerService
from segue.hasher import Hasher

from segue.proposal.services import ProposalService
from segue.proposal.errors import NoSuchProposal

from errors import NoSuchNotification, NotificationExpired, NotificationAlreadyAnswered, NoSuchSlot, SlotIsEmpty, SlotNotDirty
from models import Room, Slot, Notification, CallNotification, SlotNotification
from filters import SlotFilterStrategies

class RoomService(object):
    def get_one(self, room_id):
        return Room.query.get(room_id)

    def query(self, **kw):
        filters = kw
        return Room.query.filter(**filters).order_by(Room.position).all()

class SlotService(object):
    def __init__(self, proposals=None):
        self.proposals = proposals or ProposalService()
        self.filters = SlotFilterStrategies()

    def stretch_slot(self, slot_id):
        slot = self.get_one(slot_id, strict=True)
        next_contiguous_slot = slot.next_contiguous_slot

        if not slot.can_be_stretched:
            raise CannotBeStretched()
        if slot.next_contiguous_slot:
            db.session.delete(slot.next_contiguous_slot)

        slot.duration += 60
        db.session.add(slot)
        db.session.commit()
        return slot

    def query(self, **kw):
        base    = self.filters.joins_for(Slot.query, **kw)
        filters = self.filters.given(**kw)
        return base.filter(*filters).order_by(Slot.begins).all()

    def count(self, **kw):
        base    = self.filters.joins_for(Slot.query, **kw)
        filters = self.filters.given(**kw)
        return base.filter(*filters).count()

    def lookup(self, needle):
        base    = self.filters.all_joins(Slot.query)
        filters = self.filters.needle(needle)
        return base.filter(*filters).order_by(Slot.begins).all()

    def get_one(self, slot_id, strict=False):
        slot = Slot.query.get(slot_id)
        if slot: return slot
        elif strict: raise NoSuchSlot()
        return None

    def available_slots(self):
        return Slot.query.filter(Slot.blocked == False, Slot.talk == None).all()

    def set_talk(self, slot_id, proposal_id, annotation=None):
        slot = self.get_one(slot_id, strict=True)
        talk = self.proposals.get_one(proposal_id, strict=True)
        slot.talk = talk
        slot.status = 'dirty'
        if annotation: slot.annotation = annotation
        db.session.add(slot)
        db.session.commit()
        return slot

    def set_status(self, slot_id, new_status):
        slot = self.get_one(slot_id, strict=True)
        slot.status = new_status

        db.session.add(slot)
        db.session.commit()

        return slot

    def empty_slot(self, slot_id):
        slot = self.get_one(slot_id, strict=True)
        slot.talk = None
        slot.status = 'empty'
        db.session.add(slot)
        db.session.commit()
        return slot

    def set_blocked(self, slot_id, new_value):
        slot = self.get_one(slot_id, strict=True)
        slot.blocked = new_value
        db.session.add(slot)
        db.session.commit()
        return slot

    def annotate(self, slot_id, content):
        slot = self.get_one(slot_id, strict=True)
        slot.annotation = content
        db.session.add(slot)
        db.session.commit()
        return slot

class NotificationService(object):
    def __init__(self, mailer=None, hasher=None, proposals=None, slots=None):
        self.mailer = mailer or MailerService()
        self.hasher = hasher or Hasher()
        self.proposals = proposals or ProposalService()
        self.slots = slots or SlotService()

    def list_by_status(self, kind, status):
        return Notification.query.filter(Notification.kind == kind, Notification.status == status).all()

    def call_proposal(self, proposal_id, deadline, do_send=True):
        proposal = self.proposals.get_one(proposal_id)
        if not proposal: raise NoSuchProposal()

        already_answered = proposal.notifications.filter(Notification.status != 'pending').count() > 0
        if already_answered: raise NotificationAlreadyAnswered()

        notification = CallNotification(proposal=proposal)
        notification.account  = proposal.owner
        notification.sent     = datetime.now()
        notification.deadline = deadline
        notification.status   = 'pending'
        notification.hash     = self.hasher.generate()
        target = notification.update_target_status()

        if do_send:
            self.mailer.call_proposal(notification)

        db.session.add(target)
        db.session.add(notification)
        db.session.commit()

        return notification

    def notify_slot(self, slot_id, deadline):
        slot = self.slots.get_one(slot_id, strict=True)
        if not slot.talk: raise SlotIsEmpty()
        if slot.status != 'dirty': raise SlotNotDirty()

        already_answered = slot.notifications.filter(Notification.account == slot.talk.owner, Notification.status != 'pending').count() > 0
        if already_answered: raise NotificationAlreadyAnswered()

        notification = SlotNotification(slot=slot)
        notification.account  = slot.talk.owner
        notification.sent     = datetime.now()
        notification.deadline = deadline
        notification.status   = 'pending'
        notification.hash     = self.hasher.generate()
        target = notification.update_target_status()

        self.mailer.notify_slot(notification)

        db.session.add(target)
        db.session.add(notification)
        db.session.commit()

        return notification

    def get_by_hash(self, hash):
        notification = Notification.query.filter(Notification.hash == hash).first()
        if not notification: raise NoSuchNotification()
        return notification

    def accept_notification(self, hash):
        return self.answer_notification(hash, 'confirmed')

    def decline_notification(self, hash):
        return self.answer_notification(hash, 'declined')

    def answer_notification(self, hash, status):
        notification = self.get_by_hash(hash)
        if notification.deadline < datetime.now():
            raise NotificationExpired()
        notification.status = status
        target = notification.update_target_status()
        db.session.add(target)
        db.session.add(notification)
        db.session.commit()
        return notification
