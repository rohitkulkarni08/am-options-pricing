from google.cloud import bigquery
import pandas as pd
from config import GCP_PROJECT_ID, BIGQUERY_DATASET, BIGQUERY_TABLE

client = bigquery.Client()

def fetch_from_bigquery(ticker, start_date, end_date):
    query = f"""
        SELECT * FROM `{GCP_PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
        WHERE Ticker = '{ticker}' AND Date BETWEEN '{start_date}' AND '{end_date}'
    """
    df = client.query(query).to_dataframe()
    return df if not df.empty else None

def save_to_bigquery(ticker, data):
    data.to_gbq(destination_table=f"{BIGQUERY_DATASET}.{BIGQUERY_TABLE}",
                project_id=GCP_PROJECT_ID,
                if_exists="append")
    print(f"Data saved for {ticker} in BigQuery")
