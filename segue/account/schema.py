signup = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "email":    { "type": "string", "minLength": 5, "maxLength": 80, "format": "email" },
        "name":     { "type": "string", "minLength": 5, "maxLength": 200 },
        "password": { "type": "string", "minLength": 5, "maxLength": 200 },
    }
}

whitelist = dict(
    signup=signup
)
