import flask
from flask import request

from segue.core import config
from segue.decorators import jsoned, accepts_html

from services import JudgeService
from responses import *


class JudgeController(object):
    def __init__(self, service=None):
        self.service = service or JudgeService()

    @jsoned
    @accepts_html
    def get_by_hash(self, hash_code, wants_html=False):
        token = self.service.get_by_hash(hash_code) or flask.abort(404)

        if wants_html:
            path = '/#/judge/{}'.format(hash_code)
            return flask.redirect(config.FRONTEND_URL + path)
        else:
            return JudgeResponse.create(token), 200

    @jsoned
    def match_for_judge(self, hash_code):
        result = self.service.get_next_match_for(hash_code)
        return MatchResponse.create(result), 200

class MatchController(object):
    def __init__(self, service=None):
        self.service = service or JudgeService()

    @jsoned
    def vote_on_match(self, match_id):
        data = request.get_json()
        hash_code = data.get('hash', None)
        vote = data.get('vote', None)

        result = self.service.judge_match(match_id, hash_code, vote)
        return {}, 200
