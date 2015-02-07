import schema
from segue.factory import Factory
from models import Proposal

class ProposalFactory(Factory):
    model = Proposal

    QUERY_WHITELIST = ('owner_id',)
    UPDATE_WHITELIST = schema.edit_proposal["properties"].keys()

    @classmethod
    def clean_for_update(self, data):
        return { c:v for c,v in data.items() if c in ProposalFactory.UPDATE_WHITELIST }



