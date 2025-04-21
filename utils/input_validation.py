from datetime import datetime

def calculate_time_to_expiry(expiry_date):
    today = datetime.utcnow().date()
    expiry = datetime.strptime(expiry_date, "%Y-%m-%d").date()
    return max((expiry - today).days / 365.0, 0.0)

def default_time_to_expiry(): return 30 / 365.0
def default_volatility(ticker): return 0.2
def default_interest_rate(): return 0.03

def validate_and_find_missing_fields(entities: dict):
    validated_data = {}
    missing = []
    for field in ["Ticker", "option_type", "K", "expiry_date"]:
        if entities.get(field) is not None:
            validated_data[field] = entities[field]
        else:
            missing.append(field)
    expiry_date = entities.get("expiry_date")
    validated_data["T"] = calculate_time_to_expiry(expiry_date) if expiry_date else default_time_to_expiry()
    validated_data["sigma"] = entities.get("volatility", default_volatility(validated_data.get("Ticker")))
    validated_data["r"] = entities.get("interest rate", default_interest_rate())
    return validated_data, missing
