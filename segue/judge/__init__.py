from flask import request

from segue.core import db
from segue.json import jsoned
from segue.errors import MatchAlreadyJudged, MatchAssignedToOtherJudge, InvalidJudge, NoMatchAvailable

from models import Judge, Match
from responses import *

class JudgeService(object):
    def __init__(self, db_impl=None):
        self.db = db_impl or db

    def get_by_hash(self, hash_code):
        judge = Judge.query.filter(Judge.hash == hash_code).first()
        if not judge:
            raise InvalidJudge()
        return judge

    def get_next_match_for(self, hash_code):
        judge = self.get_by_hash(hash_code)
        match = Match.query.filter(Match.judge == judge, Match.result == None).first()
        if not match:
            match = Match.query.filter(Match.result == None).first()
            db.session.add(match)
            db.session.commit()
        return match

    def judge_match(self, match_id, hash_code, result):
        match = Match.query.get(match_id)
        if match.result != None:
            raise MatchAlreadyJudged()
        elif match.judge.hash != hash_code:
            raise MatchAssignedToOtherJudge()
        match.result = result

        db.session.add(match)
        db.session.commit()

        return match

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
