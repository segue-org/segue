import flask
from controllers import ProposalController, ProposalInviteController, NonSelectionController, TalkController

class ProposalBlueprint(flask.Blueprint):
    def __init__(self):
        super(ProposalBlueprint, self).__init__('proposals', __name__, url_prefix='/proposals')
        self.controller = ProposalController()
        self.add_url_rule('',                       methods=['POST'], view_func=self.controller.create)
        self.add_url_rule('',                       methods=['GET'],  view_func=self.controller.list)
        self.add_url_rule('/<int:proposal_id>',     methods=['GET'],  view_func=self.controller.get_one)
        self.add_url_rule('/<int:proposal_id>',     methods=['PUT'],  view_func=self.controller.modify)
        self.add_url_rule('/<string:name>.schema',  methods=['GET'],  view_func=self.controller.schema)
        self.add_url_rule('/tracks',                methods=['GET'],  view_func=self.controller.list_tracks)
        self.add_url_rule('/tracks/<int:track_id>', methods=['GET'],  view_func=self.controller.get_track)
        self.add_url_rule('/cfp-state',             methods=['GET'],  view_func=self.controller.cfp_state)

class NonSelectionBlueprint(flask.Blueprint):
    def __init__(self):
        super(NonSelectionBlueprint, self).__init__('non-selection', __name__, url_prefix='/non-selection')
        self.controller = NonSelectionController()
        self.add_url_rule('/<string:hash_code>', methods=['GET'], view_func=self.controller.get_by_hash)

class ProposalInviteBluePrint(flask.Blueprint):
    def __init__(self):
        super(ProposalInviteBluePrint, self).__init__('proposal_invites', __name__, url_prefix='/proposals/<int:proposal_id>/invites')
        self.controller = ProposalInviteController()
        self.add_url_rule('',                             methods=['GET'],   view_func=self.controller.list)
        self.add_url_rule('',                             methods=['POST'],  view_func=self.controller.create)
        self.add_url_rule('/<string:hash_code>',          methods=['GET'],   view_func=self.controller.get_by_hash)
        self.add_url_rule('/<string:hash_code>/accept',   methods=['POST'],  view_func=self.controller.accept)
        self.add_url_rule('/<string:hash_code>/decline',  methods=['POST'],  view_func=self.controller.decline)
        self.add_url_rule('/<string:hash_code>/register', methods=['POST'],  view_func=self.controller.register)

class TalkBlueprint(flask.Blueprint):
    def __init__(self):
        super(TalkBlueprint, self).__init__('talks', __name__, url_prefix='/talks')
        self.controller = TalkController()
        self.add_url_rule('/<int:talk_id>', methods=['GET'], view_func=self.controller.get_one)


