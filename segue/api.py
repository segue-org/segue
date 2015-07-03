import flask

import admin
import frontdesk

from document import DocumentBlueprint
from judge import JudgeBlueprint, MatchBlueprint
from purchase import PurchaseBlueprint, PaymentBlueprint
from account import AccountBlueprint, SessionBlueprint
from proposal import ProposalBlueprint, NonSelectionBlueprint, ProposalInviteBluePrint, TalkBlueprint
from product import ProductBlueprint
from caravan import CaravanBlueprint, CaravanInviteBluePrint
from schedule import NotificationBlueprint, RoomBlueprint, SlotBlueprint

def load_blueprints():
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
        TalkBlueprint(),
        NotificationBlueprint(),
    ]
    blueprints += admin.load_blueprints()
    blueprints += frontdesk.load_blueprints()
    return blueprints
