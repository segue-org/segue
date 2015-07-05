CPF_PATTERN = "^\d{3}.?\d{3}.?\d{3}-?\d{2}$"
CPF_CNPJ_PATTERN = r"(^\d{3}.?\d{3}.?\d{3}.?\d{2}$)|(^\d{2}.?\d{3}.?\d{3}.?\d{4}.?\d{2}$)"

new_corporate = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "name":             { "type": "string", "minLength": 3, "maxLength": 80 },
        "badge_name":       { "type": "string", "minLength": 3, "maxLength": 80 },
        "document":         { "type": "string", "minLength": 11, "maxLength": 20, "pattern": CPF_CNPJ_PATTERN },
        "address_number":   { "type": "string", "minLength": 1, "maxLength": 80 },
        "address_street":   { "type": "string", "minLength": 5, "maxLength": 80 },
        "address_extra":    { "type": "string", "minLength": 0, "maxLength": 80 },
        "address_district": { "type": "string", "minLength": 3, "maxLength": 80 },
        "address_city":     { "type": "string", "minLength": 2, "maxLength": 80 },
        "address_state":    { "type": "string", "minLength": 2, "maxLength": 80 },
        "address_zipcode":  { "type": "string", "minLength": 8, "maxLength": 8  },
        "incharge_name":    { "type": "string", "minLength": 5, "maxLength": 80 },
        "incharge_email":   { "type": "string", "minLength": 5, "maxLength": 80 },
        "incharge_phone_1": { "type": "string", "minLength": 10, "maxLength": 80 },
        "incharge_phone_2": { "type": "string", "minLength": 0, "maxLength": 80 },
    },
    "required": [
                  "name", "badge_name", "document",
                  "address_street", "address_number", "address_district",
                  "address_city", "address_state", "address_zipcode",
                  "incharge_name", "incharge_phone_1"
                ]
}
edit_corporate = new_corporate.copy()

new_employee = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "email":         { "type": "string", "minLength": 5, "maxLength": 80, "format": "email" },
        "name":          { "type": "string", "minLength": 5, "maxLength": 80 },
        "badge_name":    { "type": "string", "minLength": 5, "maxLength": 80 },
        "document":      { "type": "string", "minLength": 11, "maxLength": 11, "pattern": CPF_PATTERN },
    },
    "required": [ "email", "name", "document" ]
}

whitelist = dict(
    new_corporate = new_corporate,
    edit_corporate = edit_corporate,
    new_employee = new_employee
)
