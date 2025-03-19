def generate_forecast(validated_data: dict):
    underlying = validated_data['underlying_asset']

    # Placeholder logic
    forecast_summary = "We expect increased volatility next quarter."

    return {
        "result": f"Forecast for {underlying}: {forecast_summary}"
    }
