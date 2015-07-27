import flask

from controllers import SurveyController

class SurveyBlueprint(flask.Blueprint):
    def __init__(self):
        super(SurveyBlueprint, self).__init__('survey', __name__, url_prefix='/accounts/<int:account_id>/survey')
        self.controller = SurveyController()
        self.add_url_rule('',        methods=['GET'],  view_func=self.controller.list)
        self.add_url_rule('',        methods=['POST'], view_func=self.controller.answer)
