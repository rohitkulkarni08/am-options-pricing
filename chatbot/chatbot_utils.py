import openai
import json
import textwrap

def call_gpt(prompt: str, temperature=0.0):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"❌ GPT API call failed: {e}")
        return None

def extract_intent_and_entities(user_query: str):
    """
    Uses GPT to extract intent and entities from the user's query.
    Returns a dictionary with intent and mapped entities.
    """
    
    raw_prompt = '''
    You are an AI assistant for an American Options Pricing chatbot.

    Extract:
    1. intent: Choose from ["option_price_prediction", "exercise_probability", "forecasting"]
    2. entities: including underlying_asset (Ticker), expiry_date, strike_price, option_type (call/put)

    Return in JSON format like this:
    {
        "intent": "option_price_prediction",
        "entities": {
            "underlying_asset": "TSLA",
            "expiry_date": "2025-06-21",
            "strike_price": 700,
            "option_type": "call"
        }
    }

    User Query: "{user_query}"
    '''

    prompt = textwrap.dedent(raw_prompt).strip().format(user_query=user_query)

    response_str = call_gpt(prompt)

    if not response_str:
        return {"error": "No response from GPT"}

    try:
        response_json = json.loads(response_str)

        # Validate and map GPT output to internal schema
        intent = response_json.get("intent", "").strip()
        entities = response_json.get("entities", {})

        # Normalize entities
        mapped_entities = {
            "Ticker": entities.get("underlying_asset"),
            "expiry_date": entities.get("expiry_date"),
            "K": entities.get("strike_price"),
            "option_type": map_option_type(entities.get("option_type"))
        }

        return {
            "intent": intent,
            "entities": mapped_entities
        }

    except json.JSONDecodeError:
        print("❌ Failed to parse GPT response")
        return {"error": "Failed to parse GPT response", "raw_response": response_str}

def map_option_type(option_type_str):
    """
    Converts GPT's 'call'/'put' string to your system's numerical format.
    1 = Call, 0 = Put
    """
    if option_type_str is None:
        return None
    option_type_str = option_type_str.lower().strip()
    if option_type_str == "call":
        return 1
    elif option_type_str == "put":
        return 0
    else:
        return None
