import numpy as np
import pandas as pd

def calculate_rolling_volatility(stock_data, window=30):
    results = {}
    for ticker in stock_data['Ticker'].unique():
        ticker_data = stock_data[stock_data['Ticker'] == ticker].copy()
        if len(ticker_data) < window:
            results[ticker] = 0.20
            continue

        ticker_data['Returns'] = ticker_data['Close'].pct_change()
        rolling_volatility = ticker_data['Returns'].rolling(window).std() * np.sqrt(252)
        results[ticker] = rolling_volatility.dropna().iloc[-1] if not rolling_volatility.dropna().empty else 0.20

    return pd.Series(results)

def rsi_calc(series, window=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window=window).mean()
    loss = -delta.clip(upper=0).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_macd(series, short=12, long=26, signal=9):
    short_ema = series.ewm(span=short, adjust=False).mean()
    long_ema = series.ewm(span=long, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line


def feature_engineering(stock_data):
    stock_data['RollingVol_30d'] = calculate_rolling_volatility(stock_data)
    stock_data['RSI_14'] = stock_data.groupby('Ticker')['Close'].transform(lambda x: rsi_calc(x))
    stock_data['MACD'] = stock_data.groupby('Ticker')['Close'].transform(lambda x: get_macd(x)[0])
    stock_data['MACD_Signal'] = stock_data.groupby('Ticker')['Close'].transform(lambda x: get_macd(x)[1])
    return stock_data
