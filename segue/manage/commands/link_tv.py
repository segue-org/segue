#!/usr/bin/python
# vim: set fileencoding=utf-8

import re
import sys
import codecs
import requests

from datetime import datetime, timedelta

from segue.core import db
from segue.models import *
from segue.schedule.services import RoomService, SlotService

from support import *

#                       sala41f-high-201107011025.ogv
RE_FILE = re.compile(r'^sala(.*?)-.*-?(\d{12}).ogv')
RE_URL = re.compile(r'href="(.*.ogv)"')
MAX_DELTA = timedelta(minutes=35);
BASE_URL = 'http://hemingway.softwarelivre.org/fisl16/high/'

USAGE = """
python manage.py link_tv --rooms=40t,41a,...
"""

def link_tv(rooms_to_scan=None):
    init_command()
    if not rooms_to_scan: print USAGE; return

    rooms = RoomService()
    slots = SlotService()

    ambiguous, not_found, done = [], [], []

    print "{}*********************************{}".format(B.RED, B.RESET)
    print "{}** DELETING ALL RECORDING LINKS**{}".format(B.RED, B.RESET)
    print "{}*********************************{}".format(B.RED, B.RESET)
    Recording.query.delete()

    for room_name in rooms_to_scan.split(","):
        room = rooms.get_by_name(room_name)

        url_to_download = BASE_URL + room_name + "/"
        print "downloading: {}{}{}...".format(F.GREEN, url_to_download, F.RESET)
        result = requests.get(url_to_download)
        files = re.findall(RE_URL, result.text.strip());
        print "\tfound {}{}{} files linked".format(F.GREEN, len(files), F.RESET)

        for filename in files:
            print "\tscanning {}{}{}...".format(F.BLUE, filename, F.RESET)
            full_url = BASE_URL + room_name + '/' + filename;
            _, timestamp = re.match(RE_FILE, filename).groups();
            when = datetime.strptime(timestamp, '%Y%m%d%H%M');
            print "\t\tlooking for slots with timestamp {}{}{}".format(F.YELLOW, when, F.RESET)

            candidates = slots.by_approximate_timestamp(room.id, when)

            if not candidates:
                print "\t\t{}could not find slot!{}".format(F.RED, F.RESET)
                not_found += full_url
                continue
            elif len(candidates) > 1:
                print "\t\t{}found more than one slot!".format(F.RED, F.RESET)
                ambiguous += full_url
                continue

            slot, delta = candidates[0]
            print "\t\tfound slot: {}{}{} with delta of {}{:.0f}{} seconds".format(
                F.GREEN, slot, F.RESET,
                F.GREEN, delta.total_seconds(), F.RESET
            )
            print "\t\tcreating recoding...",
            recording = Recording(slot=slot, url=full_url)
            db.session.add(recording)
            done += full_url
            print "{}OK!{}".format(F.GREEN, F.RESET)

    print "*****************************"
    print "recordings linked: {}".format(len(done))
    print "timestamps with no slots: {}".format(len(not_found))
    print "timestamps with multiple slots: {}".format(len(ambiguous))
    print "commiting..."
    db.session.commit()
    print "OK"



class Command(object):
    def handle(self,**kw):
        print yellow('deletando registros de Recording!');
        # Recording.objects.all().delete();
        for name, id in ROOMS.items():
            print red('SALA ' + name);
            url_to_download = BASE_URL + name + "/";
            print url_to_download
            result = urllib2.urlopen(url_to_download);
            for line in result.readlines():
                files = re.findall(RE_URL, line.strip());
                for filename in files:
                    room_name, timestamp = re.match(RE_FILE, filename).groups();
                    room_id = ROOMS[room_name];
                    when = datetime.strptime(timestamp, '%Y%m%d%H%M');

                    best_slot, delta = Slot.objects.get_closest_to_timestamp(room_id, when);
                    if when.day == 24:
                        print yellow("video ignorado, dia errado!");
                        continue;

                    if not best_slot:
                        print "---";
                        print red(u'atenção'), u'slot não encontrado para o horário!'
                        print filename, room_name, timestamp;
                        print blue(full_url);
                        print "---"
                    elif best_slot.candidate == None:
                        print '---'
                        print 'SLOT VAZIO, skipping';
                        print blue(full_url);
                        print '---'
                    elif delta > MAX_DELTA:
                        print "---"
                        print red(u'atenção'), 'delta > MAX_DELTA';
                        print u"título da palestra", best_slot.candidate.activity.title;
                        print best_slot.start,;
                        print "%02dmins%02dseg" % (delta.seconds / 60, delta.seconds % 60);
                        print filename, room_name, timestamp;
                        print blue(full_url);
                        print "---"
                    else:
                        # AQUI
                        print blue(full_url), green('ok');
            print "-----------";
        print "total de sessoes linkadas:", Recording.objects.count();
