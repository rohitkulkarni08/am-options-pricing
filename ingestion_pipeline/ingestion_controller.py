import pandas as pd
from ingestion_pipeline.data_fetch import get_stock_data
from ingestion_pipeline.macro_fetch import get_risk_free_rate
from ingestion_pipeline.feature_engineering import feature_engineering
from ingestion_pipeline.event_labelling import add_shock_events
from ingestion_pipeline.database import fetch_from_bigquery, save_to_bigquery
from ingestion_pipeline.caching import fetch_from_cache, cache_data

def handle_data_request(ticker, start_date, end_date):
    """
    Handles end-to-end data retrieval, processing, and caching for a given ticker.
    """
    cache_key = generate_cache_key(ticker, start_date, end_date)

    # Step 1: Check Redis cache
    cached_data = fetch_from_cache(cache_key)
    if cached_data:
        print(f"Cache hit for {ticker}")
        return pd.DataFrame(cached_data)

    # Step 2: Check BigQuery
    existing_data = fetch_from_bigquery(ticker, start_date, end_date)
    if existing_data is not None:
        print(f"Found data in BigQuery for {ticker}")
        cache_data(cache_key, existing_data.to_dict(orient='records'))
        return existing_data

    # Step 3: Fetch & process new data
    print(f"Data missing for {ticker}, running full ingestion pipeline...")

    # Fetch historical stock data
    stock_data = get_stock_data([ticker], start_date, end_date)

    if stock_data.empty:
        print(f"No stock data fetched for {ticker}. Exiting.")
        return None

    # Apply feature engineering pipeline
    stock_data = feature_engineering(stock_data)

    # Label shock events (optional macro feature)
    stock_data = add_shock_events(stock_data)

    # Save to BigQuery and cache results
    save_to_bigquery(ticker, stock_data)
    cache_data(cache_key, stock_data.to_dict(orient='records'))

    print(f"Data ingestion complete for {ticker}")

    return stock_data

def generate_cache_key(ticker, start_date, end_date):
    """
    Generate a unique cache key for Redis caching.
    """
    return f"{ticker}|{start_date}|{end_date}"
