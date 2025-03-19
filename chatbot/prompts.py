EXTRACTION_PROMPT = """
You are an AI assistant that helps extract structured data from user queries about American options pricing.

User Query: {query}

Extract the following as JSON:
1. Intent: (Prediction / Comparison / Scenario Analysis)
2. Underlying Stock (ticker)
3. Option Type (Call/Put)
4. Strike Price (USD)
5. Current Stock Price (USD)
6. Volatility (%)
7. Interest Rate (%)
8. Time to Maturity (years)
9. Any additional constraints
"""

FOLLOW_UP_PROMPT = """
Based on the extracted information:
{extracted_data}

Confirm the inputs are correct.
Offer options:
1. Compare with another stock.
2. Show price changes if volatility or interest rate changes.
"""
