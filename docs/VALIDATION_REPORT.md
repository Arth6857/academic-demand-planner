Validation Report

1. Automated Tests

The project includes automated tests for data generation, validation, forecasting, allocation, and anomaly detection.

The latest recorded test run passed 14 tests. Rerun the test suite before submission:

pytest -v

2. Data Integrity

The validation module checks the following constraints:

* Primary-key uniqueness
* Foreign-key integrity
* Allowed values and numeric constraints
* Duplicate relationships
* Self-referencing prerequisites
* Availability date ordering

These checks help identify inconsistent or invalid synthetic academic-planning records.

3. Forecasting

The previously recorded full-scale pipeline reported the following results:

Metric	Result
Courses evaluated	1,000
Mean Absolute Error (MAE)	4.682
Root Mean Squared Error (RMSE)	5.8527
Forecast bias	0.474

These results are based on synthetic data and should not be interpreted as evidence of accuracy on real university data.

4. Allocation

The previously recorded full-scale pipeline generated 1,605 section-allocation decisions. Results should be interpreted alongside the project’s capacity, faculty-skill, and workload constraints.

5. Anomaly Detection

Five labelled anomaly scenarios were included:

* Faculty skill mismatch
* Faculty workload exceeded
* Section capacity exceeded
* Prerequisite ordering violation
* Duplicate section assignment

The previously recorded full-pipeline run detected all five scenarios. This targeted synthetic test does not establish performance on unseen anomalies.

6. Reproducibility

Repeated full-pipeline runs using seed 20261022 previously produced matching DataFrames for generated entities, allocations, and forecasts.

To reproduce the pipeline locally:

python -m pip install -r requirements.txt
python -m src.academic_planner.main --scale full
pytest -v

7. Limitations

* The data is synthetic and may not represent real university behaviour.
* Forecasting metrics depend on the synthetic data-generation process.
* Detecting the five labelled scenarios does not establish performance on unseen anomalies.
* Results have been validated locally; no real-world deployment or production-scale evaluation is claimed.

8. Validation Status

The results above reflect previously recorded runs. Rerun the pipeline and test suite before submission, and update this report if the results differ.