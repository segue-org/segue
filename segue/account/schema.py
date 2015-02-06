ACCOUNT_ROLES = [ "user","operator","admin" ]

signup = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "email":        { "type": "string", "minLength": 5,  "maxLength": 80, "format": "email" },
        "name":         { "type": "string", "minLength": 5,  "maxLength": 80 },
        "password":     { "type": "string", "minLength": 5,  "maxLength": 80 },
        "cpf":          { "type": "string", "minLength": 11, "maxLength": 14, "pattern": "^\d{3}.?\d{3}.?\d{3}.?\d{2}$" },
        "passport":     { "type": "string", "minLength": 5,  "maxLength": 15 },
        "country":      { "type": "string", "minLength": 5,  "maxLength": 30 },
        "city":         { "type": "string", "minLength": 5,  "maxLength": 30 },
        "phone":        { "type": "string", "minLength": 5,  "maxLength": 30 },
        "organization": { "type": "string", "minLength": 5,  "maxLength": 30 },
        "resume":       { "type": "string", "minLength": 5,  "maxLength": 200 },
        "role":         { "enum": ACCOUNT_ROLES }
    },
    "required": ["email", "name", "password", "country", "city", "phone" ],
}

whitelist = dict(
    signup=signup
)
