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
    "additionalProperties": False,
    "required": [ "title", "summary", "full", "language", "level" ]
}

whitelist = dict(
    new_proposal=new_proposal
)
