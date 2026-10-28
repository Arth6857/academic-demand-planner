from src.academic_planner.generator import generate_dataset
from src.academic_planner.forecasting import (
    forecast_demand,
    evaluate_forecast,
)


def test_forecast_contains_all_courses():
    dataset = generate_dataset("starter", seed=20261022)
    forecasts = forecast_demand(dataset)

    assert len(forecasts) == len(dataset["Course"])
    assert "course_id" in forecasts.columns
    assert "forecast_demand" in forecasts.columns


def test_forecast_demand_is_non_negative():
    dataset = generate_dataset("starter", seed=20261022)
    forecasts = forecast_demand(dataset)

    assert (forecasts["forecast_demand"] >= 0).all()


def test_forecast_metrics_are_finite():
    dataset = generate_dataset("starter", seed=20261022)
    forecasts = forecast_demand(dataset)
    metrics = evaluate_forecast(forecasts)

    assert metrics["course_count"] == len(dataset["Course"])
    assert metrics["mae"] >= 0
    assert metrics["rmse"] >= 0
