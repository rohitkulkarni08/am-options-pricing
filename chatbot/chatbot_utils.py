import openai
import json

def call_gpt(prompt: str, temperature=0.0):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return response['choices'][0]['message']['content']

def extract_intent_and_entities(user_query: str):
    prompt = f"""
    You are an AI assistant for an American Options Pricing chatbot.

    Extract:
    1. intent: Choose from ["option_price_prediction", "exercise_probability", "forecasting"]
    2. entities: such as underlying_asset, expiry_date, strike_price, option_type (call/put)

    Return as JSON. Example:
    {{
        "intent": "option_price_prediction",
        "entities": {{
            "underlying_asset": "TSLA",
            "expiry_date": "2025-06-21",
            "strike_price": 700,
            "option_type": "call"
        }}
    }}

    User Query: "{user_query}"
    """

    response_str = call_gpt(prompt)
    
    try:
        response_json = json.loads(response_str)
        return response_json
    except json.JSONDecodeError:
        return {"error": "Failed to parse GPT response", "raw_response": response_str}
