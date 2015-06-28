
PROPOSAL_LEVELS = ['beginner','advanced']

new_proposal = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "title":    { "type": "string", "minLength": 5, "maxLength": 80   },
        "full":     { "type": "string", "minLength": 5, "maxLength": 2000 },
        "language": { "type": "string", "minLength": 2, "maxLenght": 2 },
        "level":    { "enum": PROPOSAL_LEVELS },
        "track_id": { "type": "integer" },
    },
    "required": [ "title", "full", "language", "level" ]
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

admin_create = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "title":     { "type": "string", "minLength": 5, "maxLength": 80   },
        "full":      { "type": "string", "minLength": 5, "maxLength": 2000 },
        "language":  { "type": "string", "minLength": 2, "maxLenght": 2 },
        "level":     { "enum": PROPOSAL_LEVELS },
        "track_id":  { "type": "integer" },
        "owner_id ": { "type": "integer" },
    },
    "required": [ "title", "full", "language", "level", "owner_id", "track_id" ]
    }

whitelist = dict(
    new_proposal  = new_proposal,
    edit_proposal = edit_proposal,
    new_invite    = new_invite,
    admin_create  = admin_create
)
