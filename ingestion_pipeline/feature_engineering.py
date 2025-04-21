import pandas as pd # type: ignore
import numpy as np # type: ignore

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

def engineer_features(df):
    df = df.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values(by=['Ticker', 'Date'], inplace=True)

    df['Return'] = df.groupby('Ticker')['Close'].transform(lambda x: x.pct_change())
    df['RollingVol_30d'] = df.groupby('Ticker')['Return'].transform(
        lambda x: x.rolling(window=30).std() * np.sqrt(252))

    df['Skewness_30d'] = df.groupby('Ticker')['Return'].transform(
        lambda x: x.rolling(window=30).apply(lambda y: pd.Series(y).skew(), raw=False))
    
    df['Kurtosis_30d'] = df.groupby('Ticker')['Return'].transform(
        lambda x: x.rolling(window=30).apply(lambda y: pd.Series(y).kurt(), raw=False))

    df['RSI_14'] = df.groupby('Ticker')['Close'].transform(lambda x: rsi_calc(x))
    df['MACD'] = df.groupby('Ticker')['Close'].transform(lambda x: get_macd(x)[0])
    df['MACD_Signal'] = df.groupby('Ticker')['Close'].transform(lambda x: get_macd(x)[1])

    df['Avg_Volume_20d'] = df.groupby('Ticker')['Volume'].transform(lambda x: x.rolling(window=20, min_periods=1).mean())
    df['Avg_Volume_30d'] = df.groupby('Ticker')['Volume'].transform(lambda x: x.rolling(window=30, min_periods=1).mean())
    df['Avg_Volume_60d'] = df.groupby('Ticker')['Volume'].transform(lambda x: x.rolling(window=60, min_periods=1).mean())

    df['Relative_Volume_20d'] = df['Volume'] / df['Avg_Volume_20d']
    df['Volume_Change_1d'] = df.groupby('Ticker')['Volume'].transform(lambda x: x.pct_change())
    df['Volume_Change_5d'] = df.groupby('Ticker')['Volume'].transform(lambda x: x.pct_change(periods=5))

    return df
