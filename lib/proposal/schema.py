PROPOSAL_LEVELS = ['beginner','advanced']

new_proposal_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "title":       { "type": "string", "minLength": 5, "maxLength": 80   },
        "abstract":    { "type": "string", "minLength": 5, "maxLength": 200  },
        "description": { "type": "string", "minLength": 5, "maxLength": 2000 },
        "language":    { "type": "string", "minLength": 2, "maxLenght": 2 },
        "level":       { "enum": PROPOSAL_LEVELS },
    },
    "additionalProperties": False,
    "required": [ "title", "abstract", "description", "language", "level" ]
}
