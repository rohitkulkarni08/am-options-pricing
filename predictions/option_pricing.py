import numpy as np # type: ignore
import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore
from tensorflow.keras.models import load_model # type: ignore
import traceback
from sklearn.preprocessing import StandardScaler # type: ignore
import shap # type: ignore

def load_npz_scaler(path="scalers/options_pricing_scaler_npz.npz"):
    data = np.load(path)
    scaler = StandardScaler()
    scaler.mean_ = data["mean_"]
    scaler.scale_ = data["scale_"]
    scaler.n_features_in_ = scaler.mean_.shape[0]
    return scaler

MODEL_PATH = "models/options_pricing_model.keras"
SCALER_PATH = "scalers/options_pricing_scaler_npz.npz"

FEATURES_OPTIONS_PRICING = [
    'S0', 'K', 'T', 'sigma', 'r', 'moneyness', 'log_moneyness', 
    'RSI', 'MACD', 'Skewness', 'Kurtosis','Relative_Volume', 'Volume_Change_1d', 'Volume_Change_5d', 
    'delta', 'gamma', 'vega', 'theta', 'rho', 
    'option_type', 'sector_encoded', 
    'shock_event_binary'
]

model = load_model(MODEL_PATH)
scaler = load_npz_scaler(SCALER_PATH)

def prepare_single_row_for_pricing(df_row, scaler, feature_columns):
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

    row['sector_encoded'] = row['Sector'].astype('category').cat.codes

    shock_val = str(row.get("shock_event", ["None"])[0])
    row['shock_event_binary'] = int(shock_val != 'None' and shock_val.lower() != 'nan')

    row = row[feature_columns]

    row = row.fillna(0.0)

    assert row.shape[0] == 1, f"Expected single row, got {row.shape}"

    X_scaled = scaler.transform(row)

    return X_scaled

def predict_price_with_shap(df_row, model=model, scaler=scaler, feature_columns=FEATURES_OPTIONS_PRICING):
    try:
        if df_row.shape[0] != 1:
            raise ValueError(f"Expected single-row DataFrame, got {df_row.shape}")

        X_scaled = prepare_single_row_for_pricing(df_row, scaler, feature_columns)

        options_price = model.predict(X_scaled, verbose=0)[0][0]

        explainer = shap.Explainer(model, X_scaled)
        shap_values = explainer(X_scaled)
        shap_row = shap_values.values[0]
        shap_dict = dict(zip(feature_columns, shap_row.round(4)))

        return options_price, shap_dict

    except Exception as e:
        print("ERROR in predict_price_with_shap:")
        traceback.print_exc()
        raise e
