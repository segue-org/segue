BUYER_TYPES = ['person','company','government']
CPF_CNPJ_PATTERN = r"(^\d{3}.?\d{3}.?\d{3}.?\d{2}$)|(^\d{2}.?\d{3}.?\d{3}.?\d{4}.?\d{2}$)"

buyer = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "kind":            { "enum": BUYER_TYPES },
        "name":            { "type": "string", "minLength": 5,  "maxLength": 100 },
        "document":        { "type": "string", "minLength": 11, "maxLength": 20, "pattern": CPF_CNPJ_PATTERN },
        "contact":         { "type": "string", "minLength": 0,  "maxLength": 100 },
        "address_street":  { "type": "string", "minLength": 5,  "maxLength": 80  },
        "address_number":  { "type": "string", "minLength": 1,  "maxLength": 20  },
        "address_extra":   { "type": "string", "minLength": 0,  "maxLength": 40  },
        "address_city":    { "type": "string", "minLength": 2,  "maxLength": 60  },
        "address_country": { "type": "string", "minLength": 2,  "maxLength": 40  },
        "address_zipcode": { "type": "string", "minLength": 2,  "maxLength": 10  },
    },
    "required": [
        "kind", "name", "document",
        "address_street", "address_number", "address_city", "address_country"
    ]
}

promocode = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "hash_code": { "type": "string", "minLength": 12, "maxLength": 12 }
    },
    "required": [
        "hash_code"
    ]
}
create_promocode = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "description": { "type": "string",  "minLength": 5, "maxLength": 50 },
        "quantity":    { "type": "integer", "minimum":   1, "maximum":   100 },
        "discount":    { "type": "integer", "minimum":   0, "maximum":   100 },
        "product_id":  { "type": "integer" }
    },
    "required": [
        "description", "product_id"
    ]
}

whitelist = dict(
    buyer = buyer,
    promocode = promocode,
    create_promocode = create_promocode
)
