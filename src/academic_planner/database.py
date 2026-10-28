"""Persistence and export utilities for the academic planner."""

import hashlib
import json
import sqlite3
from pathlib import Path

from .config import RANDOM_SEED
from .generator import generate_dataset
from .validation import assert_valid_dataset


def write_json(path, records):
    """Write records as formatted JSON."""
    with path.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False, default=str)


def dataframe_checksum(df):
    """Calculate a stable checksum for a DataFrame."""
    payload = df.to_json(
        orient="records",
        date_format="iso",
        double_precision=15,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def save_entity_tables(connection, dataset):
    """Persist entity DataFrames as SQLite tables."""
    for entity, df in dataset.items():
        df.to_sql(
            entity,
            connection,
            if_exists="replace",
            index=False,
        )


def export_pipeline(
    scale="starter",
    output_dir="data/output",
    seed=RANDOM_SEED,
):
    """Run the complete workflow and export its outputs."""
    from .forecasting import forecast_demand, evaluate_forecast
    from .allocation import allocate_sections
    from .anomalies import inject_anomalies, detect_anomalies

    output_path = Path(output_dir)
    ground_truth_path = Path("data/ground_truth")
    reports_path = Path("reports")

    output_path.mkdir(parents=True, exist_ok=True)
    ground_truth_path.mkdir(parents=True, exist_ok=True)
    reports_path.mkdir(parents=True, exist_ok=True)

    # 1. Generate the baseline dataset.
    baseline = generate_dataset(scale=scale, seed=seed)
    assert_valid_dataset(baseline)

    # 2. Forecast course demand.
    forecasts = forecast_demand(baseline)
    forecast_metrics = evaluate_forecast(forecasts)

    # 3. Allocate sections, rooms, and faculty.
    allocation = allocate_sections(baseline, forecasts)

    allocated_dataset = allocation["dataset"]

    # 4. Inject controlled anomalies into a separate copy.
    anomalous_dataset, ground_truth = inject_anomalies(allocation)

    # 5. Detect anomalies.
    anomaly_report = detect_anomalies(anomalous_dataset)

    # 6. Export entity records.
    row_counts = {}

    for entity, df in allocated_dataset.items():
        df.to_csv(output_path / f"{entity}.csv", index=False)
        write_json(
            output_path / f"{entity}.json",
            df.to_dict(orient="records"),
        )
        row_counts[entity] = len(df)

    # Export forecasts, decisions, and unmet demand.
    forecasts.to_csv(output_path / "forecasts.csv", index=False)
    write_json(
        output_path / "forecasts.json",
        forecasts.to_dict(orient="records"),
    )

    allocation["decisions"].to_csv(
        reports_path / "allocation_decisions.csv",
        index=False,
    )

    allocation["unmet_demand"].to_csv(
        reports_path / "unmet_demand.csv",
        index=False,
    )

    allocation["faculty_workload"].to_csv(
        reports_path / "faculty_workload.csv",
        index=False,
    )

    anomaly_report.to_csv(
        reports_path / "anomaly_report.csv",
        index=False,
    )

    # Ground truth is deliberately kept separate.
    ground_truth.to_csv(
        ground_truth_path / "ground_truth.csv",
        index=False,
    )

    write_json(
        ground_truth_path / "ground_truth.json",
        ground_truth.to_dict(orient="records"),
    )

    # 7. Build append-only decision events for this run.
    events = []

    for index, decision in enumerate(
        allocation["decisions"].to_dict(orient="records"),
        start=1,
    ):
        events.append({
            "event_id": f"EVT-{seed}-{index:06d}",
            "entity_type": "AllocationDecision",
            "entity_id": decision.get("section_id")
            or decision.get("course_id"),
            "event_type": decision.get("decision", "UNKNOWN"),
            "reason": decision.get("reason", ""),
            "seed": seed,
        })

    for index, anomaly in enumerate(
        anomaly_report.to_dict(orient="records"),
        start=1,
    ):
        events.append({
            "event_id": f"EVT-{seed}-A{index:05d}",
            "entity_type": "Anomaly",
            "entity_id": anomaly.get("record_id", ""),
            "event_type": "ANOMALY_DETECTED",
            "reason": anomaly.get("issue_type", ""),
            "seed": seed,
        })

    events_path = reports_path / "event_history.jsonl"

    with events_path.open("w", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event) + "\n")

    # 8. Persist the valid baseline and allocation in SQLite.
    database_path = output_path / "academic_planner.db"

    with sqlite3.connect(database_path) as connection:
        save_entity_tables(connection, allocated_dataset)

        forecasts.to_sql(
            "DemandForecast",
            connection,
            if_exists="replace",
            index=False,
        )

        allocation["decisions"].to_sql(
            "AllocationDecision",
            connection,
            if_exists="replace",
            index=False,
        )

        allocation["unmet_demand"].to_sql(
            "UnmetDemand",
            connection,
            if_exists="replace",
            index=False,
        )

        import pandas as pd

        pd.DataFrame(events).to_sql(
            "EventHistory",
            connection,
            if_exists="replace",
            index=False,
        )

    # 9. Export a portable SQL seed script.
    sql_path = output_path / "seed.sql"

    with sqlite3.connect(database_path) as connection:
        with sql_path.open("w", encoding="utf-8") as file:
            for statement in connection.iterdump():
                file.write(statement + "\n")

    # 10. Record manifest and reproducibility checksums.
    checksums = {
        entity: dataframe_checksum(df)
        for entity, df in allocated_dataset.items()
    }

    manifest = {
        "scale": scale,
        "seed": seed,
        "row_counts": row_counts,
        "forecast_metrics": forecast_metrics,
        "allocation_decisions": len(allocation["decisions"]),
        "unmet_demand_records": len(allocation["unmet_demand"]),
        "detected_anomalies": len(anomaly_report),
        "ground_truth_labels": len(ground_truth),
        "checksums": checksums,
    }

    write_json(output_path / "source_manifest.json", manifest)

    return manifest