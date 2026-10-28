# Validation Report

## Automated Tests

The latest recorded test run passed 14 tests. Rerun the tests before submission to verify the current state.

## Data Integrity

The validation module checks primary-key uniqueness, foreign-key integrity, allowed values, duplicate relationships, self-prerequisites, numeric constraints, and availability date ordering.

## Anomaly Detection

Five labelled scenarios are included: faculty skill mismatch, workload exceeded, section capacity exceeded, prerequisite ordering violation, and duplicate section assignment. The previously recorded full-pipeline run detected all five scenarios.

## Reproducibility

Repeated full-pipeline runs using seed 20261022 previously produced matching DataFrames for generated entities, allocations, and forecasts.

## Limitations

Results are based on synthetic data and local tests. They do not establish performance on real university records.
