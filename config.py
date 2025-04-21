import openai # type: ignore
from google.cloud import bigquery
from google.oauth2 import service_account # type: ignore

PROJECT_ID = "hidden-brace-454217-p4"
SERVICE_ACCOUNT_PATH = "utils/service_account.json"
openai.api_key = ""

credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH)
bq_client = bigquery.Client(project=PROJECT_ID, credentials=credentials)