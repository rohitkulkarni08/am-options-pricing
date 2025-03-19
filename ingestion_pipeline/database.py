from google.cloud import bigquery
from config import GCP_PROJECT_ID, BIGQUERY_DATASET, BIGQUERY_TABLE

client = bigquery.Client(project=GCP_PROJECT_ID)

def fetch_from_bigquery(ticker, start_date, end_date):
    """
    Fetch data from BigQuery for a given ticker and date range.
    """
    query = f"""
        SELECT *
        FROM `{GCP_PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
        WHERE Ticker = @ticker
        AND Date BETWEEN @start_date AND @end_date
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("ticker", "STRING", ticker),
            bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
            bigquery.ScalarQueryParameter("end_date", "DATE", end_date)
        ]
    )

    query_job = client.query(query, job_config=job_config)
    df = query_job.to_dataframe()

    if df.empty:
        print(f" No data found for {ticker} between {start_date} and {end_date}")
        return None

    print(f" Fetched {len(df)} records for {ticker} from BigQuery")
    return df

def save_to_bigquery(ticker, data):
    """
    Save DataFrame to BigQuery.
    """
    if data.empty:
        print(f" No data to save for {ticker}")
        return

    table_id = f"{GCP_PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}"

    job = client.load_table_from_dataframe(data, table_id)

    job.result()  # Wait for the job to complete

    print(f" Data saved for {ticker} in BigQuery (Rows inserted: {len(data)})")
