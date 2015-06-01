# coding: utf-8

import codecs
import sys

from segue.judge import JudgeService
from support import *;

def invite_judges(filename, count=5, tid=0):
    init_command()
    content = open(filename, 'r').read()

    judge_service = JudgeService()

    for entry in content.split("\n"):
        token = judge_service.create_token(entry, count, tid)

        print token.__dict__
