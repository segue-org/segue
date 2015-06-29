import flask

from admin import blueprints as admin_blueprints

from document import DocumentBlueprint
from judge import JudgeBlueprint, MatchBlueprint
from purchase import PurchaseBlueprint, PaymentBlueprint
from account import AccountBlueprint, SessionBlueprint
from proposal import ProposalBlueprint, NonSelectionBlueprint, ProposalInviteBluePrint
from product import ProductBlueprint
from caravan import CaravanBlueprint, CaravanInviteBluePrint
from schedule import NotificationBlueprint, RoomBlueprint, SlotBlueprint

blueprints = [
    AccountBlueprint(),
    SessionBlueprint(),
    ProposalBlueprint(),
    NonSelectionBlueprint(),
    ProposalInviteBluePrint(),
    ProductBlueprint(),
    PurchaseBlueprint(),
    PaymentBlueprint(),
    DocumentBlueprint(),
    CaravanBlueprint(),
    CaravanInviteBluePrint(),
    JudgeBlueprint(),
    MatchBlueprint(),
    RoomBlueprint(),
    SlotBlueprint(),
    NotificationBlueprint(),
]
blueprints += admin_blueprints
