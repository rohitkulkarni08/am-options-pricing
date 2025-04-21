import yfinance as yf # type: ignore
from datetime import datetime
import requests # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore

def get_stock_data(tickers, start_date, end_date):
    all_data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        data = stock.history(start=start_date, end=end_date)

        if data.empty:
            print(f"Warning: No data found for {ticker}")
            continue

        data['Ticker'] = ticker
        all_data.append(data)

    if not all_data:
        raise ValueError("No valid stock data retrieved for tickers!")

    historical_data_combined = pd.concat(all_data)
    historical_data_combined.reset_index(inplace=True)

    return historical_data_combined

def add_shock_events(df):
    """
    Label shock events in your stock_data dataframe.
    Adds a 'shock_event' column based on date ranges.
    """

    # Initialize the column with 'None' (no shock event)
    df['shock_event'] = 'None'

    # --- Volmageddon Crash ---
    df.loc[(df['Date'] >= '2018-02-01') & (df['Date'] <= '2018-03-31'), 'shock_event'] = 'volmageddon'

    # --- 2018 Q4 Sell-Off ---
    df.loc[(df['Date'] >= '2018-10-01') & (df['Date'] <= '2018-12-31'), 'shock_event'] = '2018_q4_selloff'

    # --- COVID Crash ---
    df.loc[(df['Date'] >= '2020-02-15') & (df['Date'] <= '2020-05-01'), 'shock_event'] = 'covid_crash'

    # --- Ukraine Crisis ---
    df.loc[(df['Date'] >= '2022-02-01') & (df['Date'] <= '2022-05-01'), 'shock_event'] = 'ukraine_crisis'

    # --- Fed Hikes / Inflation Surge ---
    df.loc[(df['Date'] >= '2022-06-01') & (df['Date'] <= '2022-12-31'), 'shock_event'] = 'fed_hike_inflation'

    # --- SVB / Regional Banking Crisis ---
    df.loc[(df['Date'] >= '2023-03-01') & (df['Date'] <= '2023-06-01'), 'shock_event'] = 'svb_crisis'

    return df

def get_dividend_yield(ticker):
    """ Fetch dividend yield from Yahoo Finance """
    stock = yf.Ticker(ticker)
    return stock.info.get("dividendYield", 0) or 0.0

def get_risk_free_rate():
    """ Fetch the latest 6-month U.S. Treasury yield as a proxy for the risk-free rate """
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": "DGS6MO",  # 6-month US Treasury yield
        "api_key": "ef17cd670af1026241ee7fb83d925738",  #API key from FRED
        "file_type": "json",
        "limit": 5,  # Fetch multiple observations to ensure we get the latest one
        "sort_order": "desc"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "observations" in data and data["observations"]:
            latest_observation = max(data["observations"], key=lambda x: x["date"])
            rate = float(latest_observation["value"]) / 100
            print("Latest Risk-Free Rate:", rate)
            return rate
    return 0.05  # default fallback (5%)


def calculate_rolling_volatility(stock_data, window=30):
    """
    Calculate rolling annualized volatility for multiple tickers using historical data.
    Uses `Close` price if `Adj Close` is missing.
    """
    if stock_data.empty or 'Close' not in stock_data:
        print("Error: Stock data is missing or 'Close' not found. Returning default volatility (20%).")
        return pd.Series(0.20, index=stock_data['Ticker'].unique())  # default fallback for all tickers

    if 'Ticker' not in stock_data:
        print("Error: Missing 'Ticker' column. Cannot compute for multiple tickers.")
        return pd.Series(0.20)

    results = {}

    for ticker in stock_data['Ticker'].unique():
        ticker_data = stock_data[stock_data['Ticker'] == ticker].copy()

        if len(ticker_data) < window:
            print(f"Warning: Not enough data for {ticker} ({len(ticker_data)} days). Using default volatility.")
            results[ticker] = 0.20
            continue

        ticker_data['Price'] = ticker_data['Close']
        ticker_data['Returns'] = ticker_data['Price'].pct_change()

        if ticker_data['Returns'].isna().all():
            print(f"Error: No valid returns for {ticker}. Using default volatility.")
            results[ticker] = 0.20
            continue

        rolling_volatility = ticker_data['Returns'].rolling(window).std() * np.sqrt(252)

        if rolling_volatility.dropna().empty:
            print(f"Error: Rolling volatility calculation resulted in NaN for {ticker}. Using default.")
            results[ticker] = 0.20
            continue

        results[ticker] = rolling_volatility.dropna().iloc[-1]

    return pd.Series(results)


def calculate_time_to_expiry(expiry_date):
    """ Compute time to expiry in years """
    today = datetime.today()
    expiry = datetime.strptime(expiry_date, "%Y-%m-%d")
    return (expiry - today).days / 365.0

def get_sector(ticker):
    return yf.Ticker(ticker).info.get('sector', 'Unknown')