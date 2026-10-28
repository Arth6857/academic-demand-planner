from src.academic_planner.generator import generate_dataset
from src.academic_planner.forecasting import forecast_demand
from src.academic_planner.allocation import allocate_sections
from src.academic_planner.anomalies import (
    inject_anomalies,
    detect_anomalies,
)


def test_five_anomaly_labels_are_generated():
    dataset = generate_dataset("starter", seed=20261022)
    forecasts = forecast_demand(dataset)
    allocation = allocate_sections(dataset, forecasts)

    _, ground_truth = inject_anomalies(allocation)

    expected_types = {
        "FACULTY_SKILL_MISMATCH",
        "WORKLOAD_EXCEEDED",
        "SECTION_CAPACITY_EXCEEDED",
        "PREREQUISITE_ORDER_VIOLATION",
        "DUPLICATE_SECTION_ASSIGNMENT",
    }

    assert expected_types.issubset(set(ground_truth["issue_type"]))


def test_anomaly_detector_returns_expected_columns():
    dataset = generate_dataset("starter", seed=20261022)
    forecasts = forecast_demand(dataset)
    allocation = allocate_sections(dataset, forecasts)

    anomalous_dataset, _ = inject_anomalies(allocation)
    findings = detect_anomalies(anomalous_dataset)

    assert "issue_type" in findings.columns
    assert "record_id" in findings.columns


def test_anomaly_injection_does_not_modify_original_dataset():
    dataset = generate_dataset("starter", seed=20261022)
    forecasts = forecast_demand(dataset)
    allocation = allocate_sections(dataset, forecasts)

    original_sections = allocation["dataset"]["Section"].copy(deep=True)
    original_assignments = allocation["dataset"]["WorkloadAssignment"].copy(
        deep=True
    )

    inject_anomalies(allocation)

    assert allocation["dataset"]["Section"].equals(original_sections)
    assert allocation["dataset"]["WorkloadAssignment"].equals(
        original_assignments
    )