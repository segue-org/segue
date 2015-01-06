from factory import Sequence, LazyAttribute
from factory.alchemy import SQLAlchemyModelFactory

from lib.core import db
from lib.proposal.models import *

class SegueFactory(SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = db.session

class ValidProposalFactory(SegueFactory):
    class Meta:
        model = Proposal

    title       = Sequence(lambda n: 'Proposal Title #{0}'.format(n))
    abstract    = Sequence(lambda n: 'abstract #{0}'.format(n))
    description = Sequence(lambda n: 'description #{0}'.format(n))
    language    = 'en'
    level       = 'advanced'

class InvalidProposalFactory(ValidProposalFactory):
    # all fields fail some validation
    title       = "x"
    abstract    = "a"
    description = "d"
    language    = "xunga"
    level       = "professional"
