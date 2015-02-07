PROPOSAL_LEVELS = ['beginner','advanced']

new_proposal = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "title":    { "type": "string", "minLength": 5, "maxLength": 80   },
        "summary":  { "type": "string", "minLength": 5, "maxLength": 200  },
        "full":     { "type": "string", "minLength": 5, "maxLength": 2000 },
        "language": { "type": "string", "minLength": 2, "maxLenght": 2 },
        "level":    { "enum": PROPOSAL_LEVELS },
    },
    "required": [ "title", "summary", "full", "language", "level" ]
}
edit_proposal = new_proposal.copy()

new_invite = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "recipient": { "type": "string", "minLength": 5, "maxLength": 80, "format": "email" },
        "name":      { "type": "string", "minLength": 5, "maxLength": 80 },
    },
    "required": [ "recipient", "name" ]
}

whitelist = dict(
    new_proposal  = new_proposal,
    edit_proposal = edit_proposal,
    new_invite    = new_invite
)
