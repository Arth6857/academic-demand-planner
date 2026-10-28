"""Course demand forecasting and evaluation."""

import math

import pandas as pd


HISTORICAL_TERMS = ["2024FA", "2025SP", "2025FA", "2026SP"]
TARGET_TERM = "2026FA"

# Most recent historical period receives the largest weight.
FORECAST_WEIGHTS = [0.2, 0.3, 0.5]


def calculate_demand(dataset):
    """Calculate observed demand by course and academic term.

    REGISTERED and WAITLISTED interests count as demand.
    INTERESTED records are excluded from the primary demand measure
    because they have not yet become registrations or waitlist entries.
    """
    interests = dataset["RegistrationInterest"]

    observed = interests[
        interests["term"].isin(HISTORICAL_TERMS + [TARGET_TERM])
        & interests["status"].isin(["REGISTERED", "WAITLISTED"])
    ].copy()

    demand = (
        observed.groupby(["course_id", "term"])
        .size()
        .unstack(fill_value=0)
    )

    return demand


def forecast_demand(dataset):
    """Forecast next-term course demand using the three latest periods.

    Returns one row per course, with historical counts and a forecast.
    """
    courses = dataset["Course"]
    demand = calculate_demand(dataset)

    result = pd.DataFrame({"course_id": courses["course_id"]})

    for term in HISTORICAL_TERMS:
        if term in demand.columns:
            result[f"demand_{term}"] = (
                result["course_id"].map(demand[term]).fillna(0).astype(int)
            )
        else:
            result[f"demand_{term}"] = 0

    # Forecast from the three latest historical observations.
    terms_for_forecast = HISTORICAL_TERMS[-3:]
    weights = FORECAST_WEIGHTS

    historical_values = result[
        [f"demand_{term}" for term in terms_for_forecast]
    ].to_numpy(dtype=float)

    predictions = historical_values @ weights

    result["forecast_demand"] = [
        max(0, math.ceil(value)) for value in predictions
    ]

    # Keep the target-period outcome separate from model features.
    if TARGET_TERM in demand.columns:
        actuals = demand[TARGET_TERM]
        result["actual_demand"] = (
            result["course_id"].map(actuals).fillna(0).astype(int)
        )
    else:
        result["actual_demand"] = 0

    result["forecast_error"] = (
        result["forecast_demand"] - result["actual_demand"]
    )

    return result


def evaluate_forecast(forecast_df):
    """Calculate MAE, RMSE, and forecast bias.

    The actual outcome is used only for evaluation, never to construct
    the forecast itself.
    """
    if forecast_df.empty:
        return {
            "course_count": 0,
            "mae": 0.0,
            "rmse": 0.0,
            "bias": 0.0,
        }

    errors = (
        forecast_df["forecast_demand"]
        - forecast_df["actual_demand"]
    ).astype(float)

    mae = errors.abs().mean()
    rmse = math.sqrt((errors ** 2).mean())
    bias = errors.mean()

    return {
        "course_count": len(forecast_df),
        "mae": round(float(mae), 4),
        "rmse": round(float(rmse), 4),
        "bias": round(float(bias), 4),
    }