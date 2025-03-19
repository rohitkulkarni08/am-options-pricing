from ingestion_pipeline.ingestion_controller import handle_data_request
from ingestion_pipeline.macro_fetch import get_risk_free_rate
from chatbot_utils import parse_query, generate_follow_up

def process_chatbot_request(user_query):
    """
    Handles the chatbot query, processes input, fetches/ingests data, and returns results.
    """
    parsed_data = parse_query(user_query)

    ticker = parsed_data.get("underlying_stock")
    start_date = parsed_data.get("start_date", "2024-01-01")
    end_date = parsed_data.get("end_date", "2024-12-31")

    if not ticker:
        return {"error": "Could not extract ticker from the query."}

    # Step 1: Get data from cache/db/ingestion
    stock_data = handle_data_request(ticker, start_date, end_date)

    # Step 2: Risk-free rate
    risk_free_rate = get_risk_free_rate()

    # Step 3: Prepare chatbot response
    latest_price = stock_data['Close'].iloc[-1]

    follow_up = generate_follow_up(parsed_data)

    return {
        "ticker": ticker,
        "latest_price": latest_price,
        "risk_free_rate": risk_free_rate,
        "follow_up": follow_up,
        "parsed_data": parsed_data
    }
