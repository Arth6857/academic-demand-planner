# Academic Demand Planner

A deterministic synthetic academic planning pipeline for course-demand forecasting, section allocation, unmet-demand reporting, and anomaly detection.

## Features

- Reproducible synthetic data using seed 20261022
- Starter and full dataset configurations
- Demand forecasting and faculty allocation
- Five labelled anomaly scenarios
- CSV, JSON, SQLite, and SQL exports
- Automated tests

## Run

Install dependencies with `python -m pip install -r requirements.txt`.

Run the full pipeline with `python -m src.academic_planner.main --scale full`.

Run tests with `pytest -v`.

## Documentation

See `docs/` for the data dictionary, architecture, validation report, and AI usage documentation.

## Limitations

This project uses synthetic data and simplified planning rules. Results are intended as a demonstration, not as production scheduling recommendations.
