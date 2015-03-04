import datetime

import factory

from factory import Sequence, LazyAttribute, SubFactory
from factory.fuzzy import FuzzyChoice, FuzzyNaiveDateTime, FuzzyDecimal
from factory.alchemy import SQLAlchemyModelFactory

from segue.core import db
from segue.models import Account, Proposal, ProposalInvite, Track, Product, Purchase

def _Sequence(pattern):
    return Sequence(lambda counter: pattern.format(counter))

class SegueFactory(SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = db.session

class ValidTrackFactory(SegueFactory):
    class Meta:
        model = Track
    name_en = _Sequence('track {0}')
    name_pt = _Sequence('track {0}')
    public  = True

class ValidAccountFactory(SegueFactory):
    class Meta:
        model = Account

    email    = _Sequence('email_{0}@example.com')
    name     = _Sequence('Joaozinho {0}')
    role     = "user"
    password = "password"
    document     = "123.456.789-20"
    country      = "Brazil"
    state        = "RS"
    city         = "Porto Alegre"
    phone        = "51 2345678"
    organization = "manos da quebrada"
    resume       = "um cara legal"

class InvalidAccountFactory(ValidAccountFactory):
    email    = "email"
    name     = "nam"
    role     = "luser"
    password = "p"



class ValidProposalFactory(SegueFactory):
    class Meta:
        model = Proposal

    title       = _Sequence('Proposal Title #{0}')
    full        = _Sequence('description #{0}')
    language    = 'en'
    level       = 'advanced'

class ValidProposalWithOwnerFactory(ValidProposalFactory):
    owner = SubFactory(ValidAccountFactory)

class ValidProposalWithOwnerWithTrackFactory(ValidProposalFactory):
    owner = SubFactory(ValidAccountFactory)
    track = SubFactory(ValidTrackFactory)

class InvalidProposalFactory(ValidProposalFactory):
    title       = "x"
    full        = "d"
    language    = "xunga"
    level       = "professional"

class ValidInviteFactory(SegueFactory):
    class Meta:
        model = ProposalInvite
    proposal  = SubFactory(ValidProposalWithOwnerWithTrackFactory)
    recipient = _Sequence('fulano{0}@example.com')
    name      = _Sequence('Fulano {0}')
    status    = 'pending'
    hash      = _Sequence('DEAD{0:04x}')

class ValidProductFactory(SegueFactory):
    class Meta:
        model = Product
    kind       = FuzzyChoice(["ticket","swag"])
    category   = FuzzyChoice(["student","normal"])
    expiration = FuzzyNaiveDateTime(datetime.datetime.now(), datetime.datetime(2015,12,1,0,0,0))
    public     = True
    price      = FuzzyDecimal(70, 400, 2)

class ValidPurchaseByPersonFactory(SegueFactory):
    class Meta:
        model = Purchase

    product_id     = SubFactory(ValidProductFactory)
    customer_id    = SubFactory(ValidAccountFactory)
    status         = "pending"
    buyer_type     = 'person'
    buyer_name     = _Sequence("Pagador {0}")
    buyer_document = _Sequence("123.345.789-{0:02}")
    buyer_contact  = _Sequence("+55 23 4567-{0:04}")
    buyer_address  = _Sequence("Rua dos Bobos, numero {0}")

class ValidPurchaseByCorpFactory(SegueFactory):
    class Meta:
        model = Purchase

    product_id     = SubFactory(ValidProductFactory)
    customer_id    = SubFactory(ValidAccountFactory)
    status         = "pending"
    buyer_type     = 'company'
    buyer_name     = _Sequence("Empresa {0}")
    buyer_document = _Sequence("12.345.789/0001-{0:02}")
    buyer_contact  = _Sequence("+55 23 4000-{0:04}")
    buyer_address  = _Sequence("Av. dos Bobos, numero {0}")
