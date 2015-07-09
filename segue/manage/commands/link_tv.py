#!/usr/bin/python
# vim: set fileencoding=utf-8

import re
import sys
import codecs
import requests

from datetime import datetime, timedelta

from segue.core import db, config
from segue.models import *
from segue.schedule.services import RoomService, SlotService

from support import *

USAGE = """
python manage.py link_tv --rooms=40t,41a,...
"""

def link_tv(rooms_to_scan=None, early_max=5, late_max=25):
    init_command()

    if not rooms_to_scan: print USAGE; return
    early_max = int(early_max or 0)
    late_max  = int(late_max  or 0)

    rooms = RoomService()
    slots = SlotService()

    ambiguous, not_found, done = [], [], []

    print "{}*********************************{}".format(B.RED, B.RESET)
    print "{}** DELETING ALL RECORDING LINKS**{}".format(B.RED, B.RESET)
    print "{}*********************************{}".format(B.RED, B.RESET)
    Recording.query.delete()

    for room_name in rooms_to_scan.split(","):
        room = rooms.get_by_name(room_name)

        url_to_download = config.RECORDINGS_BASE_URL + room_name + "/"
        print "downloading: {}{}{}...".format(F.GREEN, url_to_download, F.RESET)
        result = requests.get(url_to_download)
        files = re.findall(config.RECORDINGS_LINK_PATTERN, result.text.strip());
        print "\tfound {}{}{} files linked".format(F.GREEN, len(files), F.RESET)

        for filename in files:
            print "\tscanning {}{}{}...".format(F.BLUE, filename, F.RESET)
            recording_url = url_to_download + filename;
            _, timestamp = re.match(config.RECORDINGS_FILE_PATTERN, filename).groups();
            when = datetime.strptime(timestamp, '%Y%m%d%H%M');
            print "\t\tlooking for slots with timestamp {}{}{}".format(F.YELLOW, when, F.RESET)

            candidates = slots.by_approximate_timestamp(room.id, when, early_max=early_max, late_max=late_max)

            if not candidates:
                print "\t\t{}could not find slot!{}".format(F.RED, F.RESET)
                not_found.append(recording_url)
                continue
            elif len(candidates) > 1:
                print "\t\t{}found more than one slot!".format(F.RED, F.RESET)
                ambiguous.append(recording_url)
                continue

            slot, delta = candidates[0]
            print "\t\tfound slot: {}{}{} with delta of {}{:.0f}{} seconds".format(
                F.GREEN, slot, F.RESET,
                F.GREEN, delta.total_seconds(), F.RESET
            )
            print "\t\tcreating recoding...",
            recording = Recording(slot=slot, url=recording_url)
            db.session.add(recording)
            done.append(recording_url)
            print "{}OK!{}".format(F.GREEN, F.RESET)

    print "*****************************"
    print "recordings linked: {}".format(len(done))
    print "timestamps with no slots: {}".format(len(not_found))
    print "timestamps with multiple slots: {}".format(len(ambiguous))
    print "commiting..."
    db.session.commit()
    print "OK"
