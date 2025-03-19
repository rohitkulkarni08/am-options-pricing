import numpy as np
import pandas as pd
from datetime import datetime

# === Utility Functions ===

def rsi_calc(series, window=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

def get_macd(series, short=12, long=26, signal=9):
    short_ema = series.ewm(span=short, adjust=False).mean()
    long_ema = series.ewm(span=long, adjust=False).mean()

    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal, adjust=False).mean()

    return macd, signal_line

# === Core Feature Engineering Functions ===

def add_return(stock_data):
    stock_data['Return'] = stock_data.groupby('Ticker')['Close'].transform(lambda x: x.pct_change())
    return stock_data

def add_rolling_volatility(stock_data, window=30):
    stock_data['RollingVol_30d'] = stock_data.groupby('Ticker')['Return'].transform(
        lambda x: x.rolling(window=window, min_periods=1).std() * np.sqrt(252)
    )
    return stock_data

def add_skewness_kurtosis(stock_data, window=30):
    stock_data['Skewness_30d'] = stock_data.groupby('Ticker')['Return'].transform(
        lambda x: x.rolling(window=window, min_periods=1).apply(lambda y: pd.Series(y).skew())
    )
    stock_data['Kurtosis_30d'] = stock_data.groupby('Ticker')['Return'].transform(
        lambda x: x.rolling(window=window, min_periods=1).apply(lambda y: pd.Series(y).kurt())
    )
    return stock_data

def add_rsi(stock_data, window=14):
    stock_data['RSI_14'] = stock_data.groupby('Ticker')['Close'].transform(lambda x: rsi_calc(x, window))
    return stock_data

def add_macd(stock_data):
    stock_data['MACD'] = stock_data.groupby('Ticker')['Close'].transform(lambda x: get_macd(x)[0])
    stock_data['MACD_Signal'] = stock_data.groupby('Ticker')['Close'].transform(lambda x: get_macd(x)[1])
    return stock_data

def add_volume_features(stock_data):
    stock_data['Avg_Volume_20d'] = stock_data.groupby('Ticker')['Volume'].transform(
        lambda x: x.rolling(window=20, min_periods=1).mean())
    stock_data['Avg_Volume_30d'] = stock_data.groupby('Ticker')['Volume'].transform(
        lambda x: x.rolling(window=30, min_periods=1).mean())
    stock_data['Avg_Volume_60d'] = stock_data.groupby('Ticker')['Volume'].transform(
        lambda x: x.rolling(window=60, min_periods=1).mean())

    stock_data['Relative_Volume_20d'] = stock_data['Volume'] / stock_data['Avg_Volume_20d']

    stock_data['Volume_Change_1d'] = stock_data.groupby('Ticker')['Volume'].transform(lambda x: x.pct_change())
    stock_data['Volume_Change_5d'] = stock_data.groupby('Ticker')['Volume'].transform(lambda x: x.pct_change(periods=5))

    return stock_data

# === Main Feature Engineering Pipeline ===

def feature_engineering(stock_data):
    """
    Applies the full feature engineering pipeline to stock data.
    Expects columns: Ticker, Date, Close, Volume.
    """
    stock_data = stock_data.copy()

    # Ensure correct datetime and sorting
    stock_data['Date'] = pd.to_datetime(stock_data['Date'])
    stock_data.sort_values(by=['Ticker', 'Date'], inplace=True)

    # Apply feature calculations
    stock_data = add_return(stock_data)
    stock_data = add_rolling_volatility(stock_data, window=30)
    stock_data = add_skewness_kurtosis(stock_data, window=30)
    stock_data = add_rsi(stock_data, window=14)
    stock_data = add_macd(stock_data)
    stock_data = add_volume_features(stock_data)

    return stock_data

# === Utilities for Single Row / Chatbot ===

def calculate_time_to_expiry(expiry_date):
    """
    Calculates time to expiry (T) as fraction of year.
    """
    today = datetime.utcnow().date()
    expiry = datetime.strptime(expiry_date, "%Y-%m-%d").date()
    days_to_expiry = (expiry - today).days
    T = max(days_to_expiry / 365.0, 0.0)
    return T

def default_time_to_expiry():
    """
    Default time to expiry: 30 days.
    """
    return 30 / 365.0

def default_volatility(ticker):
    """
    Default volatility: 20%
    """
    return 0.2

def default_interest_rate():
    """
    Default risk-free interest rate: 3%
    """
    return 0.03
