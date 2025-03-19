import requests
from config import FRED_API_KEY

def get_risk_free_rate():
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": "DGS6MO",
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "limit": 5,
        "sort_order": "desc"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "observations" in data and data["observations"]:
            latest_observation = max(data["observations"], key=lambda x: x["date"])
            return float(latest_observation["value"]) / 100
    return 0.05
