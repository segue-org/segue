from segue.core import db
from segue.errors import AccountAlreadyHasCorporate, NotAuthorized
from segue.hasher import Hasher
from segue.mailer import MailerService

import schema

from models import Corporate, CorporateInvite
from factories import CorporateFactory, CorporateInviteFactory, CorporateLeaderPurchaseFactory
from ..account import AccountService, Account

class CorporateService(object):
    def __init__(self, invites=None):
        self.invites = invites or CorporateInviteService(corporates=self)

    def get_one(self, corporate_id, by=None):
        result = Corporate.query.get(corporate_id)
        if self._check_ownership(result, by):
            return result
        elif result:
            raise NotAuthorized()

    def _check_ownership(self, corporate, alleged):
        if isinstance(corporate, int): corporate = self.get_one(corporate)
        return corporate and alleged and corporate.owner_id == alleged.id

    def get_by_owner(self, owner_id, by=None):
        result = Corporate.query.filter(Corporate.owner_id == owner_id).first()
        if self._check_ownership(result, by):
            return result
        elif result:
            raise NotAuthorized()

    def create(self, data, owner):
        if self.get_by_owner(owner.id, owner): raise AccountAlreadyHasCorporate()

        corporate = CorporateFactory.from_json(data, schema.new_corporate)
        corporate.owner_id = owner.id

        db.session.add(corporate)
        db.session.commit()
        return corporate

    def modify(self, corporate_id, data, by=None):
        corporate = self.get_one(corporate_id, by)

        for name, value in CorporateFactory.clean_for_update(data).items():
            setattr(corporate, name, value)
        db.session.add(corporate)
        db.session.commit()
        return corporate

    def invite_by_hash(self, hash_code):
        return self.invites.get_by_hash(hash_code)
    
    def add_invite(self, corporate_id, invite, by=None):
        return self.invites.create(corporate_id, invite, by)
        
    def update_leader_exemption(self, corporate_id, owner):
        if owner.has_valid_purchases: return None

        corporate = self.get_one(corporate_id, owner)
        if corporate.paid_riders.count() >= 5:
            purchase = CorporateLeaderPurchaseFactory.create(corporate)
            db.session.add(purchase)
            db.session.commit()
            return purchase

class CorporateInviteService(object):
    def __init__(self, corporates=None, hasher=None, accounts = None):
        self.corporates  = corporates  or CorporateService()
        self.hasher    = hasher    or Hasher()
        self.accounts  = accounts  or AccountService()

    def list(self, corporate_id, by=None):
        return self.corporates.get_one(corporate_id, by).invites

    def create(self, corporate_id, data, by=None):
        print "******** dados do create em CorporateInviteService ************"
        print data
        print "**by "
        print by
        print "******** /dados do create em CorporateInviteService ************"
        corporate = self.corporates.get_one(corporate_id, by)

        invite = CorporateInviteFactory.from_json(data, schema.new_invite)
        invite.corporate = corporate
        invite.hash    = self.hasher.generate()

        db.session.add(invite)
        db.session.commit()

        return invite

    def get_by_hash(self, invite_hash):
        return CorporateInvite.query.filter(CorporateInvite.hash == invite_hash).first()

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
