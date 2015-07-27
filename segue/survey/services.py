import os
import csv

from segue.core import db, config
from models import SurveyAnswer, Question

class SurveyService(object):
    def __init__(self, survey_root=None):
        self.root = survey_root or config.APP_PATH

    def load_survey(self, name):
        survey_path = os.path.join(self.root, name + ".csv")

        result = []
        with open(survey_path, 'rb') as survey_file:
            for index, line in enumerate(csv.reader(survey_file)):
                result.append(Question(index, *line))
        return result

    def save_answers(self, survey, answers, by_user=None):
        if not by_user: return ValueError()

        for label, answer in answers.items():
            if not answer: continue
            if self._answer_exists(by_user, label): continue
            entry = SurveyAnswer()
            entry.survey   = survey
            entry.question = label
            entry.answer   = answer
            entry.account  = by_user
            db.session.add(entry)

        db.session.commit()
        return True

    def _answer_exists(self, account, question):
        return SurveyAnswer.query.filter(SurveyAnswer.account == account, SurveyAnswer.question == question).count() > 0
