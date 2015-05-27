from flask import request

from segue.json import jsoned
from services import JudgeService
from responses import *

class JudgeController(object):
    def __init__(self, service=None):
        self.service = service or JudgeService()

    @jsoned
    def get_by_hash(self, hash_code):
        result = self.service.get_by_hash(hash_code)
        return JudgeResponse.create(result), 200

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
