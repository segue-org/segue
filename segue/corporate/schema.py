CPF_PATTERN = "^\d{3}.?\d{3}.?\d{3}-?\d{2}$"
CPF_CNPJ_PATTERN = r"(^\d{3}.?\d{3}.?\d{3}.?\d{2}$)|(^\d{2}.?\d{3}.?\d{3}.?\d{4}.?\d{2}$)"

new_corporate = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "name":        { "type": "string", "minLength": 5, "maxLength": 80 },
        "city":        { "type": "string", "minLength": 5, "maxLength": 80 },
        "document":    { "type": "string", "minLength": 11, "maxLength": 20, "pattern": CPF_CNPJ_PATTERN },
    },
    "required": [ "name", "city", "document" ]
}
edit_corporate = new_corporate.copy()

new_employee = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "email":         { "type": "string", "minLength": 5, "maxLength": 80, "format": "email" },
        "name":          { "type": "string", "minLength": 5, "maxLength": 80 },
        "document":      { "type": "string", "minLength": 11, "maxLength": 14, "pattern": CPF_PATTERN },
    },
    "required": [ "email", "name", "document" ]
}

whitelist = dict(
    new_corporate = new_corporate,
    edit_corporate = edit_corporate,
    new_employee = new_employee
)
