BUYER_TYPES = ['person','company','government']
CPF_CNPJ_PATTERN = r"(^\d{3}.?\d{3}.?\d{3}.?\d{2}$)|(^\d{2}.?\d{3}.?\d{3}.?\d{4}.?\d{2}$)"

purchase = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "buyer_type":     { "enum": BUYER_TYPES },
        "buyer_name":     { "type": "string", "minLength": 5,  "maxLength": 80 },
        "buyer_document": { "type": "string", "minLength": 11, "maxLength": 20, "pattern": CPF_CNPJ_PATTERN },
        "buyer_contact":  { "type": "string", "minLength": 5,  "maxLength": 100 },
        "buyer_address":  { "type": "string", "minLength": 5,  "maxLength": 100 }
    },
    "required": [ "buyer_type", "buyer_document", "buyer_contact", "buyer_address" ]
}

whitelist = dict(
    purchase = purchase,
)
