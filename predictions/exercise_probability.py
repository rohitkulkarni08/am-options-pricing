import numpy as np # type: ignore
import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore
from tensorflow.keras.models import load_model # type: ignore
import traceback
from sklearn.preprocessing import StandardScaler # type: ignore

def load_npz_scaler(path="scalers/early_exercise_scaler_npz.npz"):
    data = np.load(path)
    scaler = StandardScaler()
    scaler.mean_ = data["mean_"]
    scaler.scale_ = data["scale_"]
    scaler.n_features_in_ = scaler.mean_.shape[0]
    return scaler

MODEL_PATH = "models/early_exercise_model.keras"
SCALER_PATH = "scalers/early_exercise_scaler_npz.npz"

FEATURES_EXERCISE_PROBABILITY = [
    'S0', 'K', 'T', 'sigma', 'r',
    'moneyness', 'log_moneyness',
    'RSI', 'MACD', 'Skewness', 'Kurtosis',
    'Relative_Volume', 'Volume_Change_1d', 'Volume_Change_5d',
    'delta', 'gamma', 'vega', 'theta', 'rho',
    'option_type',
    'shock_event_binary'
]

model = load_model(MODEL_PATH)
scaler = load_npz_scaler(SCALER_PATH)

def prepare_single_row_for_probability(df_row, scaler, feature_columns):
    """
    Takes raw 1-row DataFrame and returns scaled input for model.
    """
    row = df_row.copy()

    row['S0'] = row['Close']
    row['moneyness'] = row['S0'] / row['K']
    row['log_moneyness'] = np.log(row['moneyness'] + 1e-6)

    row = row.rename(columns={
        'RollingVol_30d': 'sigma',
        'RSI_14': 'RSI',
        'Skewness_30d': 'Skewness',
        'Kurtosis_30d': 'Kurtosis',
        'Relative_Volume_20d': 'Relative_Volume'
    })

    shock_val = str(row.get("shock_event", ["None"])[0])
    row['shock_event_binary'] = int(shock_val != 'None' and shock_val.lower() != 'nan')

    row = row[feature_columns]

    row = row.fillna(0.0)

    assert row.shape[0] == 1, f"Expected single row, got {row.shape}"

    X_scaled = scaler.transform(row)

    return X_scaled

def predict_prob_from_raw_df(df_row, model=model, scaler=scaler, feature_columns=FEATURES_EXERCISE_PROBABILITY):
    try:
        if df_row.shape[0] != 1:
            raise ValueError(f"Expected single-row DataFrame, got {df_row.shape}")

        X_scaled = prepare_single_row_for_probability(df_row, scaler, feature_columns)
        prob = model.predict(X_scaled, verbose=0)[0][0]
        return float(np.clip(prob, 0, 1))

    except Exception as e:
        print("ERROR in predict_from_raw_df:")
        traceback.print_exc()
        raise e

# def simulate_exercise_prob_over_time(df_row, steps=30):
#     """
#     Simulate early exercise probability by reducing T over time.
#     Returns a list of (T, prob) tuples.
#     """
#     original_T = df_row["T"].values[0]
#     T_values = np.linspace(0.001, original_T, steps)
#     results = []

#     for T in T_values:
#         temp_row = df_row.copy()
#         temp_row.loc[:, "T"] = T  # Safe assignment
#         try:
#             prob = predict_prob_from_raw_df(temp_row)
#             results.append((T, prob))
#         except Exception as e:
#             print(f"⚠️ Prediction failed at T={T}: {e}")
#             continue

#     return results

# def plot_exercise_probability_curve(results, title="Exercise Probability vs. Time to Expiry"):
#     """
#     Plot results from simulate_exercise_prob_over_time().
#     """
#     T_vals, probs = zip(*results)
#     plt.figure(figsize=(8, 4))
#     plt.plot(T_vals, probs, marker='o')
#     plt.gca().invert_xaxis()
#     plt.xlabel("Time to Expiry (T)")
#     plt.ylabel("Predicted Early Exercise Probability")
#     plt.title(title)
#     plt.grid(True)
#     plt.tight_layout()
#     plt.show()
