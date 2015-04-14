new_caravan = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "name":        { "type": "string", "minLength": 5, "maxLength": 80 },
        "city":        { "type": "string", "minLength": 5, "maxLength": 80 },
        "description": { "type": "string", "minLength": 5, "maxLength": 400 }
    },
    "required": [ "name", "city" ]
}
edit_caravan = new_caravan.copy()

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
    new_caravan = new_caravan,
    edit_caravan = edit_caravan,
    new_invite = new_invite
)
