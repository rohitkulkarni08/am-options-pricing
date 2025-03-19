import yfinance as yf
import pandas as pd

# Fetch historical data
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

    historical_data_combined.sort_values(by=["Ticker", "Date"], inplace=True)
    
    return historical_data_combined

# Fetch real-time features
def fetch_current_features(ticker):
    stock = yf.Ticker(ticker)
    current_price = stock.history(period='1d')['Close'].iloc[-1]
    sector = stock.info.get('sector', 'Unknown')
    dividend = stock.info.get('dividendYield', 0.0)

    return {
        "current_stock_price": current_price,
        "sector": sector,
        "dividend_yield": dividend
    }
