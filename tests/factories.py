from factory import Factory, Sequence, LazyAttribute

from lib.core import db
from lib.proposal.models import *

class SegueFactory(Factory):

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        entity = model_class(*args, **kwargs)
        db.session.add(entity)
        db.session.commit()
        return entity

class ProposalFactory(SegueFactory):
    class Meta:
        model = Proposal

    title       = Sequence(lambda n: 'Proposal Title #{0}'.format(n))
    abstract    = Sequence(lambda n: 'abstract #{0}'.format(n))
    description = Sequence(lambda n: 'description #{0}'.format(n))
    video_authorization = True
    language = 'en'
    level = 'pro'
