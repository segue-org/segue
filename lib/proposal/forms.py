from wtforms import Form, StringField
from wtforms.validators import Length, AnyOf

PROPOSAL_LEVELS = ('beginner','advanced')

class NewProposalForm(Form):
    title       = StringField('title',       [ Length(min=5, max=80)  ])
    abstract    = StringField('abstract',    [ Length(min=5, max=200) ])
    description = StringField('description', [ Length(min=5, max=200) ])
    language    = StringField('language',    [ Length(min=2, max=2)   ])
    level       = StringField('level',       [ AnyOf(PROPOSAL_LEVELS) ])

