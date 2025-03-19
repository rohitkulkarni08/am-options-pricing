import os

# Google Cloud Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/gcp-credentials.json"
GCP_PROJECT_ID = "your-project-id"
BIGQUERY_DATASET = "your_dataset"
BIGQUERY_TABLE = "stock_data"

# Redis Cache (Optional for caching implementation)
REDIS_HOST = "your-redis-host"
REDIS_PORT = 6379

# Yahoo Finance API Key (Optional)
YAHOO_API_KEY = ""
FRED_API_KEY = "your_fred_api_key"

# Default values for fallback
DEFAULT_VOLATILITY = 0.20
DEFAULT_INTEREST_RATE = 0.05
