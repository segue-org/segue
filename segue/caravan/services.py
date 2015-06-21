from segue.core import db
from segue.hasher import Hasher
from segue.mailer import MailerService
from segue.errors import NotAuthorized

import schema

from models import Caravan, CaravanInvite
from factories import CaravanFactory, CaravanInviteFactory, CaravanLeaderPurchaseFactory
from errors import AccountAlreadyHasCaravan

from segue.account.services import AccountService

class CaravanService(object):
    def __init__(self, invites=None):
        self.invites = invites or CaravanInviteService(caravans=self)

    def get_one(self, caravan_id, by=None):
        result = Caravan.query.get(caravan_id)
        if self._check_ownership(result, by):
            return result
        elif result:
            raise NotAuthorized()

    def _check_ownership(self, caravan, alleged):
        if isinstance(caravan, int): caravan = self.get_one(caravan)
        return caravan and alleged and caravan.owner_id == alleged.id

    def get_by_owner(self, owner_id, by=None):
        result = Caravan.query.filter(Caravan.owner_id == owner_id).first()
        if self._check_ownership(result, by):
            return result
        elif result:
            raise NotAuthorized()

    def create(self, data, owner):
        if self.get_by_owner(owner.id, owner): raise AccountAlreadyHasCaravan()

        caravan = CaravanFactory.from_json(data, schema.new_caravan)
        caravan.owner = owner
        db.session.add(caravan)
        db.session.commit()
        return caravan

    def modify(self, caravan_id, data, by=None):
        caravan = self.get_one(caravan_id, by)

        for name, value in CaravanFactory.clean_for_update(data).items():
            setattr(caravan, name, value)
        db.session.add(caravan)
        db.session.commit()
        return caravan

    def invite_by_hash(self, hash_code):
        return self.invites.get_by_hash(hash_code)

    def update_leader_exemption(self, caravan_id, owner):
        if owner.has_valid_purchases: return None

        caravan = self.get_one(caravan_id, owner)
        if caravan.paid_riders.count() >= 5:
            purchase = CaravanLeaderPurchaseFactory.create(caravan)
            db.session.add(purchase)
            db.session.commit()
            return purchase

class CaravanInviteService(object):
    def __init__(self, caravans=None, hasher=None, accounts = None, mailer=None):
        self.caravans  = caravans  or CaravanService()
        self.hasher    = hasher    or Hasher()
        self.mailer    = mailer    or MailerService()
        self.accounts  = accounts  or AccountService()

    def list(self, caravan_id, by=None):
        return self.caravans.get_one(caravan_id, by).invites

    def create(self, caravan_id, data, by=None):
        caravan = self.caravans.get_one(caravan_id, by)

        invite = CaravanInviteFactory.from_json(data, schema.new_invite)
        invite.caravan = caravan
        invite.hash    = self.hasher.generate()

        db.session.add(invite)
        db.session.commit()

        self.mailer.caravan_invite(invite)

        return invite

    def get_by_hash(self, invite_hash):
        return CaravanInvite.query.filter(CaravanInvite.hash == invite_hash).first()

    def answer(self, hash_code, accepted=True, by=None):
        invite = self.get_by_hash(hash_code)
        if not invite:
            return None
        if self.accounts.is_email_registered(invite.recipient):
            if not by or by.email != invite.recipient:
                raise NotAuthorized

        invite.status = 'accepted' if accepted else 'declined'
        db.session.add(invite)
        db.session.commit()
        return invite

    def register(self, hash_code, account_data):
        invite = self.get_by_hash(hash_code)
        if not invite:
            return None
        if invite.recipient != account_data['email']:
            return NotAuthorized

        return self.accounts.create(account_data)
