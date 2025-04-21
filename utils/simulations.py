import pandas as pd # type: ignore
import numpy as np # type: ignore
from predictions.exercise_probability import predict_prob_from_raw_df
from predictions.option_pricing import predict_price_with_shap
from datetime import datetime, timedelta
import plotly.graph_objects as go # type: ignore

def simulate_and_plot_predictions(
    df_row,
    smooth=True,
    n_points=5
):
    """
    Simulates option price and early exercise probability over time.
    Displays interactive dual-line chart using Plotly.

    Args:
        df_row: Single-row input DataFrame
        model, scaler, feature_columns: used in prediction_fn
        prediction_fn: function(df_row) -> (price, exercise_prob)
        smooth: If True, simulate daily. If False, simulate n_points only.
        n_points: Used only if smooth=False

    Returns:
        pd.DataFrame with Date, Predicted_Price, Exercise_Probability
    """
    if df_row.shape[0] != 1:
        raise ValueError("df_row must have exactly one row")

    expiry_date = pd.to_datetime(df_row["expiry_date"].values[0]).normalize()
    today = pd.Timestamp.today().normalize()

    if expiry_date <= today:
        raise ValueError("expiry_date must be in the future")

    if smooth:
        date_range = pd.date_range(start=today, end=expiry_date, freq="D")
    else:
        date_range = pd.date_range(start=today, end=expiry_date, periods=n_points)

    results = []
    for current_date in date_range:
        df_sim = df_row.copy()
        T = (expiry_date - current_date).days / 365.0
        df_sim["T"] = T
        df_sim["Date"] = pd.to_datetime(current_date)

        try:
            option_price, shap_dict  = predict_price_with_shap(df_sim)
            prob = predict_prob_from_raw_df(df_sim)

            results.append({
                "Date": current_date.date(),
                "Predicted_Price": round(option_price, 4),
                "Exercise_Probability": round(prob, 4)
            })
        except Exception as e:
            print(f"Prediction failed on {current_date.date()}: {e}")
            continue

    df_results = pd.DataFrame(results)

    # plotly chart
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_results["Date"],
        y=df_results["Predicted_Price"],
        mode="lines+markers",
        name="Option Price",
        hovertemplate="Date: %{x}<br>Price: $%{y:.2f}<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=df_results["Date"],
        y=df_results["Exercise_Probability"] * 100,
        mode="lines+markers",
        name="Exercise Probability (%)",
        yaxis="y2",
        hovertemplate="Date: %{x}<br>Exercise: %{y:.2f}%<extra></extra>"
    ))

    # layout with dual y-axes
    fig.update_layout(
        title="Option Price & Early Exercise Probability Over Time",
        xaxis_title="Date",
        yaxis=dict(title="Option Price", side="left"),
        yaxis2=dict(title="Exercise Probability (%)", overlaying="y", side="right"),
        legend=dict(x=0.5, xanchor="center", orientation="h"),
        margin=dict(t=40, b=30),
        height=450
    )

    return df_results, fig
