from utils.config import bq_client

def upload_to_bigquery(latest_stock_data, project_id="hidden-brace-454217-p4", dataset_id="historical_stock_data", table_name="raw_stock_data"):
    ticker = latest_stock_data["Ticker"]
    table_id = f"{project_id}.{dataset_id}.{table_name}"

    job = bq_client.load_table_from_dataframe(latest_stock_data, table_id)
    job.result()  # Wait for completion

    print(f"Successfully loaded latest {ticker} data!!!!")
