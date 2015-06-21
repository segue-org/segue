import flask
from controllers import JudgeController, MatchController

class JudgeBlueprint(flask.Blueprint):
    def __init__(self):
        super(JudgeBlueprint, self).__init__('judges', __name__, url_prefix='/judges')
        self.controller = JudgeController()
        self.add_url_rule('/<string:hash_code>',       methods=['GET'], view_func=self.controller.get_by_hash)
        self.add_url_rule('/<string:hash_code>/match', methods=['GET'], view_func=self.controller.match_for_judge)

class MatchBlueprint(flask.Blueprint):
    def __init__(self):
        super(MatchBlueprint, self).__init__('matches', __name__, url_prefix='/matches')
        self.controller = MatchController()
        self.add_url_rule('/<int:match_id>/vote', methods=['POST'], view_func=self.controller.vote_on_match)
