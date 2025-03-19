from data_fetch import get_stock_data
from macro_fetch import get_risk_free_rate
from feature_engineering import feature_engineering
from event_labelling import add_shock_events
from database import fetch_from_bigquery, save_to_bigquery
from caching import fetch_from_cache, cache_data

def handle_data_request(ticker, start_date, end_date):
    cached_data = fetch_from_cache(ticker)
    if cached_data:
        print(f"Cache hit for {ticker}")
        return pd.DataFrame(cached_data)

    existing_data = fetch_from_bigquery(ticker, start_date, end_date)
    if existing_data is not None:
        print(f"Found data in BigQuery for {ticker}")
        cache_data(ticker, existing_data.to_dict(orient='records'))
        return existing_data

    print(f"Data missing for {ticker}, running ingestion...")
    stock_data = get_stock_data([ticker], start_date, end_date)
    stock_data = feature_engineering(stock_data)
    stock_data = add_shock_events(stock_data)

    save_to_bigquery(ticker, stock_data)
    cache_data(ticker, stock_data.to_dict(orient='records'))

    return stock_data
