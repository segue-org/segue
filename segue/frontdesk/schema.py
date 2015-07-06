CPF_PATTERN = "^\d{3}.?\d{3}.?\d{3}-?\d{2}$"

create = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "email":        { "type": "string", "minLength": 5,  "maxLength": 80, "format": "email" },
    },
    "required": [ 'email'  ]
}

visitor = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "email":  { "type": "string", "minLength": 5, "maxLength": 80, "format": "email" },
        "name":   { "type": "string", "minLength": 5, "maxLength": 80 },
    },
    "required": [ 'email', 'name' ]
}

patch = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "email":        { "type": "string", "minLength": 5,  "maxLength": 80, "format": "email" },
        "name":         { "type": "string", "minLength": 5,  "maxLength": 80 },
        "password":     { "type": "string", "minLength": 5,  "maxLength": 80 },
        "cpf":          { "type": "string", "minLength": 11, "maxLength": 14, "pattern": CPF_PATTERN },
        "document":     { "type": "string", "minLength": 5,  "maxLength": 14 },
        "passport":     { "type": "string", "minLength": 5,  "maxLength": 15 },
        "country":      { "type": "string", "minLength": 5,  "maxLength": 30 },
        "city":         { "type": "string", "minLength": 3,  "maxLength": 30 },
        "phone":        { "type": "string", "minLength": 5,  "maxLength": 30 },
        "organization": { "type": "string", "minLength": 3,  "maxLength": 30 },
        "resume":       { "type": "string", "minLength": 5,  "maxLength": 400 },
    },
    "required": [   ]
}

whitelist=dict(
    patch=patch,
    create=create,
    visitor=visitor
)
