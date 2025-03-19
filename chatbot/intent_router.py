from modules.option_price_module import predict_option_price
from modules.exercise_probability_module import calculate_exercise_probability
from modules.forecasting_module import generate_forecast

MODULE_ROUTER = {
    "option_price_prediction": predict_option_price,
    "exercise_probability": calculate_exercise_probability,
    "forecasting": generate_forecast
}

def route_intent(intent: str, validated_data: dict):
    if intent in MODULE_ROUTER:
        return MODULE_ROUTER[intent](validated_data)
    else:
        return {"error": f"Unknown intent: {intent}"}
