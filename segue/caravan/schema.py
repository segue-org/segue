create = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "name":     { "type": "string", "minLength": 5, "maxLength": 80 },
        "city":     { "type": "string", "minLength": 5, "maxLength": 80 },
    },
    "required": [ "name", "city" ]
}

whitelist = dict(
    create = create
)
