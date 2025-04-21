import pandas as pd # type: ignore
import numpy as np # type: ignore
from scipy.stats import norm # type: ignore

def calculate_baw_price(S, K, T, r, sigma, q=0.0, option_type="put"):
    try:
        S = float(S)
        K = float(K)
        T = float(T)
        r = float(r)
        sigma = float(sigma)
        q = float(q)
    except Exception as e:
        raise ValueError(f"Type conversion failed in BAW inputs: {e}")

    epsilon = 1e-5

    try:
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        euro_put = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        euro_call = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

        M = 2 * r / sigma**2
        N = 2 * (r - q) / sigma**2

        if option_type == "call":
            q2 = (-(N - 1) + np.sqrt((N - 1)**2 + 4 * M)) / 2
        else:
            q2 = (-(N - 1) - np.sqrt((N - 1)**2 + 4 * M)) / 2

        if np.abs(q2) < epsilon:
            q2 = -epsilon

        denom = 1 - 1 / q2
        if np.abs(denom) < epsilon:
            denom = -epsilon

        S_critical = K / denom

        if option_type == "put":
            if S <= S_critical:
                return K - S
            A2 = (1 - np.exp(- (r - q) * T) * norm.cdf(-d1)) * S_critical / q2
            return euro_put + A2 * (S / S_critical) ** q2
        else:  # call
            if S >= S_critical:
                return S - K
            A2 = (np.exp(- (r - q) * T) * norm.cdf(d1) - 1) * S_critical / q2
            return euro_call + A2 * (S / S_critical) ** q2

    except Exception as e:
        raise RuntimeError(f"BAW formula crashed: {e}")


def finite_diff(param, S, K, T, r, sigma, option_type='put', h=1e-4):
    if param == 'S':
        f_plus = calculate_baw_price(S + h, K, T, r, sigma, option_type)
        f_minus = calculate_baw_price(S - h, K, T, r, sigma, option_type)
    elif param == 'sigma':
        f_plus = calculate_baw_price(S, K, T, r, sigma + h, option_type)
        f_minus = calculate_baw_price(S, K, T, r, sigma - h, option_type)
    elif param == 'T':
        f_plus = calculate_baw_price(S, K, T + h, r, sigma, option_type)
        f_minus = calculate_baw_price(S, K, T - h, r, sigma, option_type)
    elif param == 'r':
        f_plus = calculate_baw_price(S, K, T, r + h, sigma, option_type)
        f_minus = calculate_baw_price(S, K, T, r - h, sigma, option_type)
    else:
        raise ValueError("Invalid param name")
    return (f_plus - f_minus) / (2 * h)

def second_finite_diff(param, S, K, T, r, sigma, option_type='put', h=1e-4):
    if param != 'S':
        raise ValueError("Only 'S' supported in second_finite_diff")
    f_plus = calculate_baw_price(S + h, K, T, r, sigma, option_type)
    f = calculate_baw_price(S, K, T, r, sigma, option_type)
    f_minus = calculate_baw_price(S - h, K, T, r, sigma, option_type)
    return (f_plus - 2 * f + f_minus) / (h ** 2)

def calculate_greeks(S, K, T, r, sigma, option_type="call"):
    epsilon = 1e-5
    if T <= 0 or sigma <= 0:
        intrinsic = max(0, S - K) if option_type == "call" else max(0, K - S)
        return {
            'price': intrinsic,
            'delta': 1.0 if option_type == "call" and intrinsic > 0 else (-1.0 if intrinsic > 0 else 0.0),
            'gamma': 0.0,
            'vega': 0.0,
            'theta': 0.0,
            'rho': 0.0
        }

    price = calculate_baw_price(S, K, T, r, sigma, q=0.0, option_type=option_type)
    delta = finite_diff('S', S, K, T, r, sigma, option_type)
    gamma = second_finite_diff('S', S, K, T, r, sigma, option_type)
    vega = finite_diff('sigma', S, K, T, r, sigma, option_type)
    theta = finite_diff('T', S, K, T, r, sigma, option_type)
    rho = finite_diff('r', S, K, T, r, sigma, option_type)

    return {
        'delta': delta,
        'gamma': gamma,
        'vega': vega / 100,
        'theta': theta / 365,
        'rho': rho / 100
    }

def safe_float(val, fallback=None):
    try:
        return float(val)
    except (ValueError, TypeError):
        return fallback

def prepare_model_input(latest_row_df: pd.DataFrame, validated_data: dict) -> pd.DataFrame:
    validated_df = pd.DataFrame([validated_data]).rename(columns={"sigma": "sigma_1"})
    merged = pd.merge(latest_row_df, validated_df, on="Ticker", how="inner")
    row = merged.iloc[0]

    try:
        S0 = safe_float(row["Close"])
        K = safe_float(row["K"])
        T = safe_float(row["T"])
        r = safe_float(row["r"])
        sigma = safe_float(row["RollingVol_30d"])
        option_type = int(row["option_type"])
    except Exception as e:
        raise ValueError(f"Failed to prepare inputs: {e}")

    greeks = calculate_greeks(S0, K, T, r, sigma, option_type)

    for greek, value in greeks.items():
        merged[greek] = value

    return merged