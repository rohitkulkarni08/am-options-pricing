from ingestion_controller import handle_data_request

if __name__ == "__main__":
    ticker = "TSLA"
    start_date = "2024-01-01"
    end_date = "2024-12-31"

    stock_data = handle_data_request(ticker, start_date, end_date)

    stock_data.to_csv(f"{ticker}_processed_stock_data.csv", index=False)
    print(f"Ingestion complete for {ticker}.")
