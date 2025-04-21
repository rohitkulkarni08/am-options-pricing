import json
import re
import openai # type: ignore

def json_parser(gpt_output):
    if isinstance(gpt_output, dict):
        return gpt_output
    cleaned = re.sub(r"^```json\s*|\s*```$", "", gpt_output.strip(), flags=re.IGNORECASE)
    try:
        return json.loads(cleaned)
    except Exception:
        return {"error": "Failed to parse", "raw": gpt_output}

def call_gpt(prompt: str, temperature=0.0):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600,
        temperature=0.0
    )
    return response.choices[0].message.content.strip()

def map_option_type(option_type_str):
    if option_type_str is None: return None
    s = option_type_str.lower().strip()
    return 1 if s == "call" else 0 if s == "put" else None

def convert_markdown_headings_to_html(text: str) -> str:
    return re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)

def extract_intent_and_entities(user_query: str):
    prompt = f'''
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
    response = call_gpt(prompt)
    response_json = json_parser(response)
    

    intent = response_json.get("intent")
    entities = {
        "Ticker": response_json.get("underlying_asset"),
        "expiry_date": response_json.get("expiry_date"),
        "K": response_json.get("strike_price"),
        "S0": response_json.get("spot_price"),
        "option_type": map_option_type(response_json.get("option_type")),
        "r": response_json.get("interest_rate"),
        "volatility": response_json.get("volatility")
    }
    return {"intent": intent, "entities": entities}



def generate_comprehensive_model_summary(input_features: dict, predicted_price: float, feature_contributions: dict):
    input_features_rounded = {
        k: round(v, 4) if isinstance(v, float) else v for k, v in input_features.items()
    }
    feature_contributions_rounded = {
        k: round(v, 4) if isinstance(v, float) else v for k, v in feature_contributions.items()
    }

    option_type_str = "Call" if input_features_rounded.get("option_type", 1) == 1 else "Put"

    prompt = f"""
You are a financial assistant explaining the prediction of an American-style {option_type_str.lower()} option using model-generated insights. Your explanation is for a smart, non-expert user who wants to understand why the model predicted a price of ${predicted_price:.2f} for this option.

You are given:
- The exact input features used by the model
- The relative contribution of each feature to the final prediction (do NOT mention them directly)

Use only the values provided in the input. Do not invent or assume anything, especially about the stock price, strike price, date, or volatility.

---

### Model Inputs:
{input_features_rounded}

### Feature Contributions (for your reasoning only — do NOT reference them in the output):
{feature_contributions_rounded}

---

### Instructions:

Write a clear, accurate, and natural-language explanation covering the following:

---

1. **Summary of the Contract**  
   - Describe the type of option (call or put), whether it is in-the-money or out-of-the-money (based on the stock price vs. strike price), the expiration timeline, and basic stock context.  
   - Use only the numbers provided. For example, say “the option is out-of-the-money because the strike price is higher than the current stock price” if that is the case.  
   - Do not restate variable names or column names (like "S0" or "option_type").  
   - **Do not use any Markdown formatting or symbols** such as asterisks (`*`), underscores (`_`), or backticks (`` ` ``).  
   - Do not bold, italicize, bullet, or number any part of the response.  
   - Write all output in plain text. Pretend this will be shown in a plain-text terminal with no formatting support.


**Key Drivers of the Price**  
   - Use the feature contributions to explain what likely influenced the predicted price.  
   - Discuss the impact of volatility, interest rates, time to expiry, moneyness, and technical indicators (like momentum or recent price changes) — but only if they are present in the input.  
   - Use plain English — for example, say "the option is near expiration, which reduces its value" or "high volatility tends to raise the price of options."

---

**Market Conditions**  
   - Reflect on how the broader market context might affect the option’s value.  
   - If RSI or MACD suggests bearish or bullish momentum, interpret it accordingly.  
   - Do not introduce any values not already present.

---

**Final Takeaway**  
   - Summarize why this option is priced the way it is.  
   - Offer a brief comment on what could change the price — e.g., a rise in volatility, a move in the stock price, or more time remaining.

---

### Rules — Do Not:

- Do not mention variable or column names from code (like option_type, S0, K, etc.)
- Do not reference SHAP, model internals, or AI/ML concepts
- Use bold (double asterisks) for section headings only, like **Summary of the Contract**, **Key Drivers of the Price**, **Market Conditions**, and **Final Takeaway**.
- Do not bold, italicize, bullet, or number anything else in the response.
- Do not use underscores (`_`), single asterisks (`*`), backticks (`\``), or any other Markdown for inline emphasis.
- Do not hallucinate or infer values — only use what's explicitly in the input
- Do not contradict the provided data
- Do not copy input values word-for-word — interpret them instead

---

Begin your explanation now, using professional and conversational language.
"""
    return call_gpt(prompt)


def generate_option_timeline_summary(df_results):
    """
    Generates a natural language summary of option price and early exercise probability over time.
    Suitable for display in a Streamlit app for a non-technical audience.

    Input:
        df_results: pd.DataFrame with columns ['Date', 'Predicted_Price', 'Exercise_Probability']
    Output:
        summary string (from GPT)
    """

    # Get metadata
    n_points = len(df_results)
    max_prob = df_results["Exercise_Probability"].max()
    max_prob_date = df_results.loc[df_results["Exercise_Probability"].idxmax(), "Date"]

    prompt = f"""
You are a financial assistant helping a user understand the performance of their American-style option over time.

The user simulated the predicted price and probability of early exercise for the option between today and its expiry. You are provided the full dataset below.

Each row contains:
- A date
- The predicted price of the option on that day
- The probability (%) that the model suggests the option may be exercised early on that date

---

### Data (Length = {n_points} points):
{df_results.round(4).to_dict(orient="records")}

---

### Instructions:

Write a clear, helpful, and beginner-friendly explanation that includes:

1. A summary of how the **option price** changes over time (e.g., is it rising, falling, flat?)
2. A summary of how the **exercise probability** changes — is it consistently low, rising, peaking?
3. Tell the user if early exercise **is recommended** at any point:
   - If yes, specify the **best date to exercise** (the one with the highest probability)
   - If no, explain that it’s best to hold until expiry and why
4. Use conversational, professional tone (no finance jargon)
5. Don’t overuse numbers — describe trends, not raw data
6. Keep your response under 3–4 short paragraphs

---

### Additional Notes:
- The highest early exercise probability is {max_prob:.2%} on {max_prob_date}.
- If that probability is below ~10%, you should recommend **not exercising early**.
- Do not mention any internal model details or code-like formatting.
- Assume this is being shown in a dashboard to a smart, non-technical person.

Write the explanation now.
"""
    return call_gpt(prompt)