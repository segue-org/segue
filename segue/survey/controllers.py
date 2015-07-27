import flask

from flask import request
from flask.ext.jwt import current_user

from segue.core import config
from segue.decorators import jsoned, jwt_only

from services import SurveyService
from responses import SurveyQuestionResponse

class SurveyController(object):
    def __init__(self, service=None):
        self.service      = service or SurveyService()
        self.current_user = current_user

    @jwt_only
    @jsoned
    def list(self, account_id):
        result = self.service.load_survey(config.DEFAULT_SURVEY)
        return SurveyQuestionResponse.create(result), 200

    @jwt_only
    @jsoned
    def answer(self, account_id):
        answers = request.get_json().get('answers', None)
        if not answers: flask.abort(400)
        result = self.service.save_answers(config.DEFAULT_SURVEY, answers, by_user=self.current_user)
        return {}, 200
