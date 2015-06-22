from datetime import datetime

from segue.core import db
from segue.mailer import MailerService
from segue.hasher import Hasher

from segue.proposal.services import ProposalService
from segue.proposal.errors import NoSuchProposal

from errors import NoSuchNotification, NotificationExpired, NotificationAlreadyAnswered, NoSuchSlot
from models import Room, Slot, Notification, CallNotification
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

    def of_room(self, room_id):
        return Slot.query.filter(Slot.room_id == room_id).all()

    def get_one(self, slot_id, strict=False):
        slot = Slot.query.get(slot_id)
        if slot: return slot
        elif strict: raise NoSuchSlot()
        return None

    def set_talk(self, slot_id, proposal_id):
        slot = self.get_one(slot_id, strict=True)
        proposal = self.proposals.get_one(proposal_id, strict=True)

        slot.proposal = proposal
        db.session.add(slot)
        db.session.commit()
        return slot

    def empty_slot(self, slot_id):
        slot = self.get_one(slot_id, strict=True)
        slot.proposal = None
        db.session.add(slot)
        db.session.commit()
        return slot

class NotificationService(object):
    def __init__(self, mailer=None, hasher=None, proposals=None):
        self.mailer = mailer or MailerService()
        self.hasher = hasher or Hasher()
        self.proposals = proposals or ProposalService()

    def list_by_status(self, kind, status):
        return Notification.query.filter(Notification.kind == kind, Notification.status == status).all()

    def call_proposal(self, proposal_id, deadline):
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

        self.mailer.call_proposal(notification)

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
