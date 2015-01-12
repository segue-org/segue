ACCOUNT_ROLES = [ "user","operator","admin" ]

signup = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "email":    { "type": "string", "minLength": 5, "maxLength": 80, "format": "email" },
        "name":     { "type": "string", "minLength": 5, "maxLength": 200 },
        "password": { "type": "string", "minLength": 5, "maxLength": 200 },
        "role":     { "enum": ACCOUNT_ROLES }
    },
    "required": ["email","name","password","role"]
}

whitelist = dict(
    signup=signup
)
