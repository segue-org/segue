class ProposalService(object):
    def __init__(self, db=None):
        pass

    def get_one(self, proposal_id):
        return { "proposal_id": proposal_id }

service = ProposalService()
