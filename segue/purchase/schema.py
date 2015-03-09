BUYER_TYPES = ['person','company','government']
CPF_CNPJ_PATTERN = r"(^\d{3}.?\d{3}.?\d{3}.?\d{2}$)|(^\d{2}.?\d{3}.?\d{3}.?\d{4}.?\d{2}$)"

buyer = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "kind":           { "enum": BUYER_TYPES },
        "name":           { "type": "string", "minLength": 5,  "maxLength": 80 },
        "document":       { "type": "string", "minLength": 11, "maxLength": 20, "pattern": CPF_CNPJ_PATTERN },
        "contact":        { "type": "string", "minLength": 5,  "maxLength": 100 },
        "address_street":  { "type": "string" },
        "address_number":  { "type": "string" },
        "address_extra":   { "type": "string" },
        "address_city":    { "type": "string" },
        "address_country": { "type": "string" },
    },
    "required": [
        "kind", "document", "contact",
        "address_street", "address_number", "address_city", "address_country"
    ]
}

whitelist = dict(
    buyer = buyer,
)
