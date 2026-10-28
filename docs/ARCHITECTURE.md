# Architecture

## Pipeline

1. Generate synthetic academic data using a fixed random seed.
2. Validate keys, relationships, allowed values, and business constraints.
3. Forecast course demand from historical registration interest.
4. Allocate sections using room capacity, faculty skills, availability, workload, and scheduling constraints.
5. Inject labelled anomalies and evaluate detection.
6. Export datasets, forecasts, allocation decisions, and reports.

## Modules

- config.py: dataset configuration and random seed.
- generator.py: synthetic data generation.
- validation.py: data integrity checks.
- forecasting.py: demand forecasting and evaluation.
- allocation.py: section and faculty allocation.
- anomalies.py: anomaly injection and detection.
- database.py: database and export functionality.
- main.py: pipeline entry point.
