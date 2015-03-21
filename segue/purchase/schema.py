BUYER_TYPES = ['person','company','government']
CPF_CNPJ_PATTERN = r"(^\d{3}.?\d{3}.?\d{3}.?\d{2}$)|(^\d{2}.?\d{3}.?\d{3}.?\d{4}.?\d{2}$)"

buyer = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "kind":            { "enum": BUYER_TYPES },
        "name":            { "type": "string", "minLength": 5,  "maxLength": 50 },
        "document":        { "type": "string", "minLength": 11, "maxLength": 20, "pattern": CPF_CNPJ_PATTERN },
        "contact":         { "type": "string", "minLength": 5,  "maxLength": 100 },
        "address_street":  { "type": "string", "minLength": 5,  "maxLength": 80  },
        "address_number":  { "type": "string", "minLength": 1,  "maxLength": 20  },
        "address_extra":   { "type": "string", "minLength": 1,  "maxLength": 40  },
        "address_city":    { "type": "string", "minLength": 2,  "maxLength": 60  },
        "address_country": { "type": "string", "minLength": 2,  "maxLength": 40  },
    },
    "required": [
        "kind", "name", "document",
        "address_street", "address_number", "address_city", "address_country"
    ]
}

whitelist = dict(
    buyer = buyer,
)
