from datetime import datetime, date

import factory
from factory import Sequence, LazyAttribute, SubFactory
from factory.fuzzy import FuzzyChoice, FuzzyDate, FuzzyNaiveDateTime, FuzzyDecimal
from factory.alchemy import SQLAlchemyModelFactory

from segue.core import db
from segue.models import Account, ResetPassword
from segue.models import ProposalTag, Proposal, ProposalInvite, Track
from segue.models import Product, CaravanProduct, StudentProduct
from segue.models import Purchase, Buyer, Payment, Transition
from segue.models import PagSeguroPayment, BoletoPayment
from segue.models import Judge, Match, Tournament
from segue.models import Room, Slot, CallNotification, SlotNotification
from segue.caravan.models import Caravan, CaravanRiderPurchase, CaravanInvite

import logging
logger = logging.getLogger('factory')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

def _Sequence(pattern):
    return Sequence(lambda counter: pattern.format(counter))

class SegueFactory(SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = db.session

class ValidTrackFactory(SegueFactory):
    class Meta:
        model = Track
    name_en = _Sequence('zona - track {0}')
    name_pt = _Sequence('zone - track {0}')
    public  = True

class ValidRoomFactory(SegueFactory):
    class Meta:
        model = Room
    name        = _Sequence('sala {0}')
    capacity    = 200
    translation = False

class ValidSlotFactory(SegueFactory):
    class Meta:
        model = Slot
    room      = SubFactory(ValidRoomFactory)
    blocked   = False
    begins    = datetime(2015,7,8,9,0,0)
    duration  = 60
    status    = 'empty'

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

class ValidTournamentFactory(SegueFactory):
    class Meta:
        model = Tournament
    name      = "fisl16"
    selection = "*"
    status    = "open"

class ValidJudgeFactory(SegueFactory):
    class Meta:
        model = Judge
    hash       = _Sequence('C0FFEE{0:04x}')
    email      = _Sequence('email_{0}@example.com')
    votes      = 5
    tournament = SubFactory(ValidTournamentFactory)

class ValidAdminAccountFactory(ValidAccountFactory):
    role = "admin"

class ValidResetFactory(SegueFactory):
    class Meta:
        model = ResetPassword
    hash    = _Sequence('C0FFEE{0:04x}')
    spent   = False
    account = SubFactory(ValidAccountFactory)


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

class ValidProposalTagFactory(SegueFactory):
    class Meta:
        model = ProposalTag
    name = _Sequence('proposal tag #{0}')

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
    kind        = FuzzyChoice(["ticket","swag"])
    category    = "normal"
    sold_until  = FuzzyNaiveDateTime(datetime.now(), datetime(2015,12,1,0,0,0))
    public      = True
    price       = FuzzyDecimal(70, 400, 2)
    description = "ingresso fisl16 - lote 1 - muggles"

class ValidCaravanProductFactory(ValidProductFactory):
    class Meta:
        model = CaravanProduct
    category    = "caravan"

class ValidStudentProductFactory(ValidProductFactory):
    class Meta:
        model = StudentProduct
    category    = "student"

class ValidBuyerFactory(SegueFactory):
    class Meta:
        model = Buyer

    address_street  = "Rua dos Bobos"
    address_number  = _Sequence("#{0}")
    address_extra   = _Sequence("apto #{0}")
    address_zipcode = _Sequence("90909-#{0:03}")
    address_city    = "Porto Alegre"
    address_country = "Brasil"

class ValidBuyerCompanyFactory(ValidBuyerFactory):
    kind     = "company"
    name     = _Sequence("Empresa {0}")
    document = _Sequence("12.345.789/0001-{0:02}")
    contact  = _Sequence("+55 23 4000-{0:04}")

class ValidBuyerPersonFactory(ValidBuyerFactory):
    kind     = 'person'
    name     = _Sequence("Pagador {0}")
    document = _Sequence("123.345.789-{0:02}")
    contact  = _Sequence("+55 23 4567-{0:04}")

class ValidPurchaseFactory(SegueFactory):
    class Meta:
        model = Purchase
    product  = SubFactory(ValidProductFactory)
    customer = SubFactory(ValidAccountFactory)
    status   = "pending"

class ValidPurchaseByPersonFactory(ValidPurchaseFactory):
    buyer = SubFactory(ValidBuyerPersonFactory)

class ValidPurchaseByCorpFactory(SegueFactory):
    buyer = SubFactory(ValidBuyerCompanyFactory)

class ValidPaymentFactory(SegueFactory):
    class Meta:
        model = Payment

    purchase = SubFactory(ValidPurchaseFactory)
    amount   = FuzzyDecimal(70, 400, 2)
    status   = "pending"

class ValidPagSeguroPaymentFactory(ValidPaymentFactory):
    class Meta:
        model = PagSeguroPayment
    reference = 'A00555-PU00444'
    code      = 'LECODE'

class ValidBoletoPaymentFactory(ValidPaymentFactory):
    class Meta:
        model = BoletoPayment
    our_number    = 101234
    due_date      = FuzzyDate(date.today())
    document_hash = _Sequence("C0FFE#{:04d}")

class ValidTransitionFactory(SegueFactory):
    class Meta:
        model = Transition
    payment = SubFactory(ValidPaymentFactory)

class ValidTransitionToPaidFactory(ValidTransitionFactory):
    old_status = 'pending'
    new_status = 'paid'

class ValidTransitionToPendingFactory(ValidTransitionFactory):
    old_status = 'started'
    new_status = 'pending'

class ValidCaravanFactory(SegueFactory):
    class Meta:
        model = Caravan
    name  = _Sequence('Caravana dos Enxutos #{:04d}')
    city  = 'Enxutolandia'

class ValidCaravanWithOwnerFactory(ValidCaravanFactory):
    owner = SubFactory(ValidAccountFactory)

class ValidCaravanInviteFactory(SegueFactory):
    class Meta:
        model = CaravanInvite
    caravan   = SubFactory(ValidCaravanWithOwnerFactory)
    recipient = _Sequence('beltrano{0}@example.com')
    name      = _Sequence('Beltrano {0}')
    status    = FuzzyChoice(['pending','accepted','declined', 'cancelled'])
    hash      = _Sequence("C0FFE#{:04d}")

class ValidCaravanPurchaseFactory(ValidPurchaseFactory):
    class Meta:
        model = CaravanRiderPurchase
    caravan = SubFactory(ValidCaravanWithOwnerFactory)

class ValidMatchFactory(SegueFactory):
    class Meta:
        model = Match
    round      = 1
    player1    = SubFactory(ValidProposalWithOwnerWithTrackFactory)
    player2    = SubFactory(ValidProposalWithOwnerWithTrackFactory)
    tournament = SubFactory(ValidTournamentFactory)

class ValidCallNotificationFactory(SegueFactory):
    class Meta:
        model = CallNotification
    proposal = SubFactory(ValidProposalWithOwnerWithTrackFactory)
    account  = SubFactory(ValidAccountFactory)
    status   = 'pending'
    hash     = _Sequence('C0FFE#{:04d}')

class ValidSlotNotificationFactory(SegueFactory):
    class Meta:
        model = SlotNotification
    slot     = SubFactory(ValidSlotFactory)
    account  = SubFactory(ValidAccountFactory)
    status   = 'pending'
    hash     = _Sequence('C0FFE#{:04d}')
