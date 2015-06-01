# coding: utf-8

import codecs
import sys

from segue.mailer import MailerService
from segue.judge.services import JudgeService, TournamentService
from support import *;

def invite_judges(filename, count=5, tid=0):
    init_command()
    content = open(filename, 'r').read()

    judge_service = JudgeService()
    mailer_service = MailerService()

    for entry in content.split("\n"):
        token = judge_service.create_token(entry, count, tid)
        print F.GREEN, "created token", F.RED, token.hash, F.RESET
        mailer_service.invite_judge(token)

def create_tournament(selection="*"):
    init_command()

    service = TournamentService()
    tournament = service.create_tournament(selection)

    print F.GREEN, "created tournament {} with selection {}".format(tournament.id, tournament.selection)

