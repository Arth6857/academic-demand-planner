# cat > tests/test_allocation.py <<'PY'
from src.academic_planner.generator import generate_dataset
from src.academic_planner.forecasting import forecast_demand
from src.academic_planner.allocation import allocate_sections


def test_allocation_returns_expected_outputs():
    dataset = generate_dataset("starter", seed=20261022)
    forecasts = forecast_demand(dataset)

    result = allocate_sections(dataset, forecasts)

    assert "dataset" in result
    assert "decisions" in result
    assert "unmet_demand" in result
    assert "faculty_workload" in result


def test_section_ids_are_unique():
    dataset = generate_dataset("starter", seed=20261022)
    forecasts = forecast_demand(dataset)

    result = allocate_sections(dataset, forecasts)
    sections = result["dataset"]["Section"]

    if not sections.empty:
        assert sections["section_id"].is_unique


def test_allocated_sections_reference_existing_courses_and_rooms():
    dataset = generate_dataset("starter", seed=20261022)
    forecasts = forecast_demand(dataset)

    result = allocate_sections(dataset, forecasts)
    allocated_dataset = result["dataset"]
    sections = allocated_dataset["Section"]

    assert sections["course_id"].isin(
        allocated_dataset["Course"]["course_id"]
    ).all()

    assert sections["room_id"].isin(
        allocated_dataset["Room"]["room_id"]
    ).all()
