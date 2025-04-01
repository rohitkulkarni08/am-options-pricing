import openai
import json
import textwrap

def json_parser(gpt_output):
    if isinstance(gpt_output, dict):
        return gpt_output

    # Remove ```json ... ``` wrappers
    cleaned = re.sub(r"^```json\s*|\s*```$", "", gpt_output.strip(), flags=re.IGNORECASE)

    try:
        return json.loads(cleaned)
    except Exception as e:
        print("JSON parse failed:", e)
        return {"error": "Failed to parse", "raw": gpt_output}

def call_gpt(prompt: str, temperature = 0.0):
    """
    Function to score the resume based on the job description using GPT model
    :param resume_text: Resume text
    :param job_description: Job description text
    :return: Score for the resume
    """
    response = openai.ChatCompletion.create(
            model= "gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens = 512,
            temperature = 0
    )
    gpt_output = response.choices[0].message.content.strip()
    return json_parser(gpt_output)

def extract_intent_and_entities(user_query: str):
    """
    Uses GPT to extract intent and entities from the user's query.
    Returns a dictionary with intent and mapped entities.
    """
    raw_prompt = f'''
    You are an AI assistant for an American Options Pricing chatbot.

    Extract the following fields as a **flat JSON** object:
    - intent: Choose from ["option_price_prediction", "exercise_probability", "forecasting"]
    - underlying_asset: the stock ticker (e.g., AAPL)
    - expiry_date: the option expiry date (ISO format)
    - strike_price: numeric
    - spot_price: numeric (optional)
    - option_type: "call" or "put"
    - interest rate: numeric (optional)
    - volatility: numeric (optional)

    User Query: {user_query}
    The output should strictly follow the JSON format and should not contain any additional information. No additional information, comments, suggestions should be included in the output. JSON output:"""
    '''

    response_json = call_gpt(raw_prompt)

    if not response_json:
        return {"error": "No response from GPT"}

    try:
        # Validate and map GPT output to internal schema
        intent = response_json.get("intent")

        # Normalize entities
        mapped_entities = {
            "Ticker": response_json.get("underlying_asset"),
            "expiry_date": response_json.get("expiry_date"),
            "K": response_json.get("strike_price"),
            "S0": response_json.get("spot_price"),
            "option_type": map_option_type(response_json.get("option_type")),
            "r": response_json.get("interest_rate"),
            "volatility": response_json.get("volatility")
        }

        return {
            "intent": intent,
            "entities": mapped_entities
        }

    except json.JSONDecodeError:
        print("Failed to parse GPT response")
        return {"error": "Failed to parse GPT response", "raw_response": response_json}

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
