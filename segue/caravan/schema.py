create = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "name":     { "type": "string", "minLength": 5, "maxLength": 80 },
        "city":     { "type": "string", "minLength": 5, "maxLength": 80 },
    },
    "required": [ "name", "city" ]
}

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
    create = create,
    new_invite = new_invite
)
