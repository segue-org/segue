import sys
import collections

import csv
import codecs

from support import *

from segue.proposal.services import ProposalService
from segue.account.services import AccountService
from segue.schedule.services import SlotService

def list_speakers(start=0, end=sys.maxint):
    init_command()

    accounts = AccountService().by_range(int(start), int(end)).all()
    result = []

    for account in accounts:
        if account.is_speaker:
            print account.email

def list_talks(room_id=None, outfile=None, day=None):
    if not room_id: print "must specify room_id"
    if not outfile: print "must specify outfile"

    service = SlotService()

    if day:
        result = service.query(room=room_id, status='confirmed', day=day)
    else:
        result = service.query(room=room_id, status='confirmed')

    with codecs.open(outfile, 'wb') as csvfile:
        output = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)

        for slot in result:
            slot_fields = [ slot.room.id, slot.begins.day, slot.begins.hour, u(slot.room.name), u(slot.talk.title) ]
            owner_row = slot_fields + [ u(slot.talk.owner.name), slot.talk.owner.email ]
            output.writerow(owner_row)
            for coauthor in slot.talk.coauthor_accounts:
                coauthor_row = slot_fields + [ u(coauthor.name), coauthor.email ]
                output.writerow(coauthor_row)

def list_proposals(start=0, end=sys.maxint, outfile='/dev/stdout'):

    proposals = ProposalService().by_range(int(start), int(end))

    with codecs.open(outfile,'wb') as csvfile:
        output = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        output.writerow("id,title,player,rejected,approved,by_public,invited,presented,noshow".split(','))

        for proposal in proposals:
            approved = proposal.tagged_as('approved'),
            marked   = proposal.tagged_as('marked') or proposal.tagged_as('marked-2'),

            line = [ proposal.id, u(proposal.title) ]
            flags = [
                proposal.tagged_as('player'),
                proposal.tagged_as('rejected'),
                marked and not approved,
                proposal.is_talk and not marked and not approved,
                proposal.was_presented
            ]
            output.writerow(line + [ int(v) for v in flags ])
