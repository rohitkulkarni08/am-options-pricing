from google.cloud import bigquery
from utils.config import bq_client
from datetime import datetime, timedelta
import pandas as pd # type: ignore
from pandas.tseries.offsets import BDay # type: ignore

def get_dynamic_start_date(last_available_date=None, default_start="2021-01-01"):
    if last_available_date is None:
        return pd.to_datetime(default_start).strftime("%Y-%m-%d")
    next_day = pd.to_datetime(last_available_date) + BDay(1)
    return next_day.strftime("%Y-%m-%d")

def get_latest_market_date(today=None):
    today = today or datetime.utcnow().date()
    if today.weekday() == 6:  # Sunday
        return today - timedelta(days=2)
    elif today.weekday() == 5:  # Saturday
        return today - timedelta(days=1)
    return today

## Old Function
def fetch_from_bigquery(validated_tuple, lookback_days=60):
    validated_data, _ = validated_tuple
    ticker = validated_data["Ticker"]
    start_date = datetime.utcnow() - timedelta(days=lookback_days)

    query = """
    SELECT * FROM `hidden-brace-454217-p4.historical_stock_data.raw_stock_data`
    WHERE ticker = @ticker AND Date >= @start_date
    ORDER BY Date ASC
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("ticker", "STRING", ticker),
            bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_date)
        ]
    )
    query_job = bq_client.query(query, job_config=job_config)
    df = query_job.to_dataframe()
    if df.empty:
        return None, True, None
    else:
        return df, False, datetime.utcnow().date()

## New Function
# def fetch_from_bigquery(validated_tuple, lookback_days=60):
#     validated_data, _ = validated_tuple
#     ticker = validated_data["Ticker"]
#     start_date = datetime.utcnow() - timedelta(days=lookback_days)

#     query = """
#     SELECT * FROM `hidden-brace-454217-p4.historical_stock_data.raw_stock_data`
#     WHERE ticker = @ticker AND Date >= @start_date
#     ORDER BY Date ASC
#     """
#     job_config = bigquery.QueryJobConfig(
#          query_parameters=[
#             bigquery.ScalarQueryParameter("ticker", "STRING", ticker),
#             bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_date)
#         ]
#     )

#     query_job = bq_client.query(query, job_config=job_config)
#     df = query_job.to_dataframe()

#     if df.empty:
#         return None, True, None

#     last_date = pd.to_datetime(df["Date"]).max().date()
#     needs_update = last_date < get_latest_market_date()
#     return df, needs_update, last_date
