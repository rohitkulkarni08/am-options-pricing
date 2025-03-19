def validate_fields(entities: dict):
    errors = []
    
    required_fields = ["underlying_asset", "expiry_date", "strike_price", "option_type"]

    for field in required_fields:
        if field not in entities or not entities[field]:
            errors.append(f"Missing required field: {field}")

    return entities, errors
