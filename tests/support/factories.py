import factory

from factory import Sequence, LazyAttribute
from factory.alchemy import SQLAlchemyModelFactory

from segue.core import db
from segue.models import *

def _Sequence(pattern):
    return Sequence(lambda counter: pattern.format(counter))

def encrypt_password(v):
    # TODO proper encryption
    return v

class SegueFactory(SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = db.session

class ValidProposalFactory(SegueFactory):
    class Meta:
        model = Proposal

    title       = _Sequence('Proposal Title #{0}')
    summary     = _Sequence('abstract #{0}')
    full        = _Sequence('description #{0}')
    language    = 'en'
    level       = 'advanced'

class InvalidProposalFactory(ValidProposalFactory):
    # all fields fail some validation
    title       = "x"
    summary     = "a"
    full        = "d"
    language    = "xunga"
    level       = "professional"

class ValidAccountFactory(SegueFactory):
    class Meta:
        model = Account

    email    = _Sequence('email_{0}@example.com')
    name     = _Sequence('Joaozinho {0}')
    password = "password"
    role     = "user"

class InvalidAccountFactory(ValidAccountFactory):
    email    = "email"
    name     = "nam"
    password = "1"
    role     = "luser"
