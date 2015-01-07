import factory

from factory import Sequence, LazyAttribute
from factory.alchemy import SQLAlchemyModelFactory

from segue.core import db
from segue.proposal.models import *

class SegueFactory(SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = db.session

class ValidProposalFactory(SegueFactory):
    class Meta:
        model = Proposal

    title       = Sequence(lambda n: 'Proposal Title #{0}'.format(n))
    summary     = Sequence(lambda n: 'abstract #{0}'.format(n))
    full        = Sequence(lambda n: 'description #{0}'.format(n))
    language    = 'en'
    level       = 'advanced'

class InvalidProposalFactory(ValidProposalFactory):
    # all fields fail some validation
    title       = "x"
    summary     = "a"
    full        = "d"
    language    = "xunga"
    level       = "professional"
