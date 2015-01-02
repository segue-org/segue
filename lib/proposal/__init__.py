import flask

class ProposalService(object):
    def __init__(self, db=None):
        pass

    def get_one(self, proposal_id):
        return { "proposal_id": proposal_id }


class ProposalController(object):
    def __init__(self, service=None):
        self.service = service or ProposalService()

    def get_one(self, proposal_id):
        return flask.jsonify(self.service.get_one(proposal_id))
