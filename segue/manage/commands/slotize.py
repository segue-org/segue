# encoding: utf-8
import sys
from collections import defaultdict
from datetime import datetime

from segue.proposal.services import ProposalService
from segue.judge.services import RankingService
from segue.schedule.services import SlotService
from support import *;

def slotize(tid=0, commit=False):
    init_command()

    total = ProposalService().query(status='confirmed')
    slotted = filter(lambda x:     x.slotted, total)
    pending = filter(lambda x: not x.slotted, total)

    ranking = RankingService().classificate(int(tid), status='confirmed', slotted=False)
    free_slots = SlotService().available_slots()

    sorted_slots = sorted(free_slots, key=slot_value, reverse=True)

    print "=========== STARTING SLOTIZE ============="
    print "TOTAL OF TALKS: {}{}{}  ".format(F.GREEN, len(total), F.RESET)
    print "ALREADY SLOTTED: {}{}{} ".format(F.GREEN, len(slotted), F.RESET)
    print "SLOT PENDING: {}{}{}    ".format(F.GREEN, len(pending), F.RESET)
    print "TOTAL FREE SLOTS: {}{}{}".format(F.GREEN, len(free_slots), F.RESET)

    for idx, ranked in enumerate(ranking):
        slot = sorted_slots[idx]
        print "{}{}{}: proposal with rank {}{}{} gets slot {}{}{} at room {}{}{} (value={}{}{})".format(
                F.RED, idx, F.RESET,
                F.GREEN, ranked.rank, F.RESET,
                F.GREEN, slot.begins, F.RESET,
                F.GREEN, slot.room.name, F.RESET,
                F.GREEN, slot_value(slot), F.RESET
        )
        if commit:
            message = 'slotize, rank {}, run {}'.format(ranked.rank, datetime.now())
            SlotService().set_talk(slot.id, ranked.proposal.id, annotation=message)

def slot_value(slot):
    value = 0
    if slot.room.capacity > 200:
        value += 1
    if slot.begins.hour in (13,14,15):
        value += 1
    elif slot.begins.hour in (16,17):
        value += 2
    elif slot.begins.hour in (9,10,18,19):
        value -= 1
    if slot.begins.day == 8:
        value -= 1
    return value
