from ingestion_pipeline.feature_engineering import (
    calculate_time_to_expiry,
    default_time_to_expiry,
    default_volatility,
    default_interest_rate
)

def validate_and_find_missing_fields(entities: dict):
    """
    Validates fields and finds missing ones. Provides defaults where possible.
    """

    validated_data = {}
    missing_fields = []

    # === Mandatory Fields (based on your flow)
    mandatory_fields = ["Ticker", "option_type", "K", "S0"]

    for field in mandatory_fields:
        if field in entities and entities[field] is not None:
            validated_data[field] = entities[field]
        else:
            missing_fields.append(field)

    # === Time to Expiry (T) ===
    expiry_date = entities.get("expiry_date")

    if expiry_date:
        validated_data["T"] = calculate_time_to_expiry(expiry_date)
    else:
        validated_data["T"] = default_time_to_expiry()

    # === Volatility (sigma) ===
    sigma = entities.get("sigma")
    validated_data["sigma"] = sigma if sigma is not None else default_volatility(validated_data.get("Ticker"))

    # === Interest Rate (r) ===
    interest_rate = entities.get("r")
    validated_data["r"] = interest_rate if interest_rate is not None else default_interest_rate()

    # === Optional: Print what fields are missing ===
    if missing_fields:
        print(f"Missing required fields: {missing_fields}")

    return validated_data, missing_fields
