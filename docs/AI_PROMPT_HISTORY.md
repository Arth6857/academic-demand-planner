"AI Prompt History — Academic Demand Planner"

1. Overview

Project: Academic Demand Planner
AI tool used: ChatGPT by OpenAI
Purpose: Assistance with project planning, implementation guidance, debugging, testing, documentation, and final submission preparation.

ChatGPT was used as an assistance tool during development. The project was implemented and tested locally, and the author remains responsible for reviewing the implementation, understanding the design decisions, and validating the results.

Record classification

This document includes reconstructed prompts representing the development tasks. They are not claimed to be verbatim copies of the original prompts.

The original ChatGPT conversation history should be consulted to recover the exact wording of every prompt submitted during development. This reconstructed record must not be treated as a complete verbatim history.

⸻

2. Project Planning and Architecture

Prompt 1: Project architecture

Reconstructed prompt

I am developing an Academic Demand Planner for a technical challenge. Help me design a modular Python application that generates synthetic academic data, forecasts course demand, allocates faculty and sections, validates data integrity, detects anomalies, and exports results. Recommend a maintainable project structure, define module responsibilities, and identify the main execution workflow. Explain the reasoning behind the architecture and identify important assumptions.

Development objective: Establish a modular structure and separate data generation, validation, forecasting, allocation, anomaly detection, and export responsibilities.

Prompt 2: Dataset design

Reconstructed prompt

Help me design a relational synthetic dataset for academic demand planning. Include programs, courses, prerequisites, student plans, registration interests, faculty, faculty skills, availability, sections, rooms, and workload assignments. Define suitable identifiers, relationships, important attributes, allowed values, and business constraints. Make the dataset suitable for reproducible generation, validation, forecasting, and allocation.

Development objective: Define the entities and relationships needed to support the planning workflow.

Prompt 3: Dataset scale and reproducibility

Reconstructed prompt

Design a deterministic synthetic data generator with configurable starter and full dataset sizes. The full configuration should support 100 programs, 1,000 courses, 500 faculty members, and 20,000 student plans. Use a fixed random seed, preserve referential integrity, generate realistic relationships, and make repeated runs reproducible. Explain how to verify reproducibility.

Development objective: Create repeatable test data at different scales.

⸻

3. Data Generation and Validation

Prompt 4: Synthetic data generation

Reconstructed prompt

Help implement a Python data generator for the academic planning entities. Ensure generated identifiers are consistent, foreign-key relationships are valid, registration interests cover multiple academic terms, and faculty skills and availability support downstream allocation. Keep the implementation deterministic and compatible with automated tests.

Development objective: Generate related synthetic entities that can be consumed by subsequent pipeline stages.

Prompt 5: Data integrity validation

Reconstructed prompt

Help design a reusable validation module for the generated academic dataset. Check primary-key uniqueness, missing identifiers, foreign-key integrity, allowed categorical values, duplicate business relationships, self-referential prerequisites, numeric constraints, and availability date ordering. Return actionable validation findings and provide a way to fail the pipeline when invalid data is detected.

Development objective: Identify data-quality issues before forecasting or allocation.

⸻

4. Demand Forecasting

Prompt 6: Historical-demand forecasting

Reconstructed prompt

Help implement a transparent course-demand forecasting baseline using historical registration-interest data. Aggregate relevant registration statuses by course and academic term, calculate a weighted forecast from historical periods, prevent negative predictions, and evaluate predictions against target-period actual demand. Include MAE, RMSE, and forecast bias, and explain the assumptions and limitations of the approach.

Development objective: Produce explainable demand estimates and measurable forecasting errors.

Prompt 7: Forecast evaluation and leakage review

Reconstructed prompt

Review the forecasting workflow for potential target leakage. Explain how to separate historical inputs from target-period actual demand, ensure actual demand is used only for evaluation, and prevent evaluation-only columns from influencing allocation decisions. Recommend tests that verify the separation between forecasting inputs, predictions, and evaluation results.

Development objective: Improve the validity and interpretability of the forecast evaluation.

⸻

5. Section and Faculty Allocation

Prompt 8: Allocation design

Reconstructed prompt

Help implement a deterministic section-allocation algorithm using forecast course demand, target section sizes, room capacities, faculty skills, faculty availability, workload limits, and scheduling conflicts. Explain how to select feasible rooms and qualified faculty, how to track assignments, and how to report demand that cannot be allocated. Make the decisions explainable and testable.

Development objective: Build a constraint-aware baseline allocation workflow.

Prompt 9: Unmet demand and infeasible allocations

Reconstructed prompt

Review an academic allocation algorithm for cases where suitable rooms or qualified faculty are unavailable. Recommend how to represent unmet demand, record allocation decisions, distinguish room-related failures from faculty-related failures, and avoid reporting demand as fulfilled when no feasible assignment exists. Identify useful edge cases for testing.

Development objective: Make allocation failures visible rather than silently treating infeasible allocations as successful.

⸻

6. Anomaly Injection and Detection

Prompt 10: Labelled anomaly generation

Reconstructed prompt

Help design controlled anomaly injection for an academic scheduling dataset. Include faculty assigned outside their skill set, faculty workload exceeding its limit, section capacity violations, prerequisite-ordering violations, and duplicate section-faculty assignments. Preserve a separate ground-truth label dataset and avoid mixing anomaly labels into normal model inputs.

Development objective: Create known test cases for evaluating anomaly detection.

Prompt 11: Anomaly detector evaluation

Reconstructed prompt

Help implement an anomaly detector for the five labelled scheduling scenarios. Ensure that detected findings can be compared with ground-truth labels, duplicate assignments are identified correctly, and the output contains useful anomaly types and affected records. Explain how to measure detection performance and identify limitations when evaluating on a small, deliberately injected set of anomalies.

Development objective: Verify whether the detector identifies the expected synthetic anomalies.

⸻

7. Database and Output Generation

Prompt 12: Data export and persistence

Reconstructed prompt

Help design a Python export workflow that saves generated academic entities and planning results in appropriate CSV and JSON formats, creates a SQLite database, produces SQL seed data, and writes supporting reports and a source manifest. Ensure the output structure is understandable, repeatable, and documented for someone running the project locally.

Development objective: Make generated data and planning results accessible for inspection.

⸻

8. Testing and Debugging

Prompt 13: Automated testing

Reconstructed prompt

Help create automated tests for the academic demand-planning pipeline. Cover deterministic data generation, dataset validation, forecasting calculations, allocation constraints, unmet demand, and anomaly detection. Use small fixtures where possible and include tests for both normal operation and important failure cases.

Development objective: Verify individual components and catch regressions.

Prompt 14: Debugging implementation issues

Reconstructed prompt

Help investigate implementation errors in the academic planning project. Identify the underlying cause before proposing changes, recommend the smallest appropriate fix, and explain how to verify it. Avoid unrelated refactoring and ensure that changes do not break previously passing tests or alter deterministic behavior unexpectedly.

Development objective: Resolve implementation issues while preserving working functionality.

Prompt 15: Reproducibility verification

Reconstructed prompt

Help verify that the academic planning pipeline is reproducible. Run the generation, forecasting, and allocation workflow repeatedly with the same seed and compare the resulting DataFrames. Identify which outputs should match and explain how to report the reproducibility results and any limitations.

Development objective: Establish repeatability under a fixed configuration.

⸻

9. Documentation and Submission Preparation

Prompt 16: README and setup instructions

Reconstructed prompt

Help prepare a clear README for the Academic Demand Planner. Document prerequisites, dependency installation, starter and full execution commands, automated tests, output locations, architecture, reproducibility, and known limitations. Ensure the commands match the actual project structure and avoid claiming functionality that has not been implemented or tested.

Development objective: Enable a reviewer to understand and run the project independently.

Prompt 17: Validation report

Reconstructed prompt

Help structure a validation report for the academic planning pipeline. Separate automated-test results, data-integrity checks, forecast metrics, allocation outcomes, anomaly-detection findings, reproducibility evidence, and known limitations. Clearly distinguish measured results from assumptions and previously observed results from newly verified results.

Development objective: Provide evidence that makes the implementation easier to evaluate.

Prompt 18: AI disclosure and final review

Reconstructed prompt

Help prepare a transparent AI usage disclosure for the project. Explain the areas where AI assistance was used, the importance of human review, how implementation results were validated, and the limitations of any reconstructed prompt history. Identify final checks needed before publishing the repository and submitting it for evaluation.

Development objective: Document AI assistance honestly and prepare a reproducible submission.

⸻

10. Human Review and Validation

AI-generated suggestions were not treated as proof of correctness. The implementation was run locally and checked through automated tests.

The development record includes a test run with 14 passing tests and a previous full-pipeline run that detected five labelled synthetic anomaly scenarios. These are historical results and should be reconfirmed before being reported as final results.

The author should be prepared to explain:

* The architecture and responsibilities of the modules.
* How the synthetic dataset and relationships are generated.
* The forecasting method and evaluation metrics.
* The allocation constraints and representation of unmet demand.
* How anomalies are injected, detected, and evaluated.
* The automated tests and reproducibility procedure.
* The assumptions, limitations, and potential improvements.

11. Completeness and Limitations

This document is a reconstructed development-task record, not a verified verbatim export of the original ChatGPT prompts.

To satisfy the challenge requirement to include all submitted prompts, the original ChatGPT conversation history must be reviewed and the actual prompts recovered. Any additional AI tools used during development must be documented separately.

No reconstructed prompt should be represented as an exact original prompt unless verified against the original conversation.