"""Controlled anomaly injection and detection."""

import pandas as pd


def inject_anomalies(allocation_result):
    """Inject five labelled anomalies into a copy of allocated data."""
    dataset = {
        name: df.copy(deep=True)
        for name, df in allocation_result["dataset"].items()
    }

    ground_truth = []
    sections = dataset["Section"].copy()
    assignments = dataset["WorkloadAssignment"].copy()
    faculty = dataset["Faculty"]
    skills = dataset["FacultySkill"]
    courses = dataset["Course"]
    prerequisites = dataset["Prerequisite"]
    rooms = dataset["Room"]

    # ANM-001: Faculty assigned to a course outside their skill set.
    if not sections.empty and not faculty.empty:
        section = sections.iloc[0]
        course_id = section["course_id"]

        qualified = set(
            skills.loc[skills["course_id"] == course_id, "faculty_id"]
        )
        unqualified = faculty[
            ~faculty["faculty_id"].isin(qualified)
        ]

        if not unqualified.empty:
            faculty_id = unqualified.iloc[0]["faculty_id"]
            record_id = "WLA-2026-900001"

            assignments = pd.concat(
                [
                    assignments,
                    pd.DataFrame([{
                        "workload_assignment_id": record_id,
                        "section_id": section["section_id"],
                        "faculty_id": faculty_id,
                        "weekly_hours": 3,
                        "status": "CONFIRMED",
                        "created_at": "2026-10-28T00:00:00",
                    }]),
                ],
                ignore_index=True,
            )

            ground_truth.append({
                "anomaly_id": "ANM-001",
                "issue_type": "FACULTY_SKILL_MISMATCH",
                "entity": "WorkloadAssignment",
                "record_id": record_id,
                "expected_detection": True,
            })

    # ANM-002: Exceed faculty workload without adding a duplicate assignment.
    if not assignments.empty and not faculty.empty:
        confirmed = assignments[
            assignments["status"] == "CONFIRMED"
        ]

        if not confirmed.empty:
            target = confirmed.iloc[0]
            faculty_id = target["faculty_id"]

            faculty_row = faculty.loc[
                faculty["faculty_id"] == faculty_id
            ].iloc[0]

            record_id = target["workload_assignment_id"]
            original_hours = int(target["weekly_hours"])
            overloaded_hours = (
                int(faculty_row["max_weekly_hours"]) + 5
            )

            assignments.loc[
                assignments["workload_assignment_id"] == record_id,
                "weekly_hours",
            ] = overloaded_hours

            ground_truth.append({
                "anomaly_id": "ANM-002",
                "issue_type": "WORKLOAD_EXCEEDED",
                "entity": "WorkloadAssignment",
                "record_id": record_id,
                "expected_detection": True,
                "original_hours": original_hours,
                "injected_hours": overloaded_hours,
            })

    # ANM-003: Section capacity is insufficient for its target enrollment.
    if not sections.empty:
        index = sections.index[0]
        original_capacity = int(sections.loc[index, "capacity"])
        sections.loc[index, "capacity"] = 1

        ground_truth.append({
            "anomaly_id": "ANM-003",
            "issue_type": "SECTION_CAPACITY_EXCEEDED",
            "entity": "Section",
            "record_id": sections.loc[index, "section_id"],
            "expected_detection": True,
            "original_capacity": original_capacity,
            "injected_capacity": 1,
        })

    # ANM-004: A course is scheduled before its prerequisite.
    if not prerequisites.empty and not courses.empty:
        prerequisite = prerequisites.iloc[0]
        dependent_course = prerequisite["course_id"]
        required_course = prerequisite["required_course_id"]

        # Ensure both courses have sections so the violation is detectable.
        for course_id in [dependent_course, required_course]:
            if not (sections["course_id"] == course_id).any():
                course_sections = sections[
                    sections["course_id"] == sections["course_id"]
                ]
                course = courses.loc[
                    courses["course_id"] == course_id
                ]

                if not course.empty:
                    template = (
                        course_sections.iloc[0].to_dict()
                        if not course_sections.empty
                        else None
                    )

                    if template is not None:
                        new_section = template.copy()
                        new_section["section_id"] = (
                            f"SEC-2026-90000{len(sections) + 1}"
                        )
                        new_section["course_id"] = course_id
                        new_section["scheduled_date"] = "2026-10-01"
                        new_section["capacity"] = min(
                            int(new_section["capacity"]), 1
                        )
                        sections = pd.concat(
                            [sections, pd.DataFrame([new_section])],
                            ignore_index=True,
                        )

        dependent = sections[
            sections["course_id"] == dependent_course
        ]
        required = sections[
            sections["course_id"] == required_course
        ]

        if not dependent.empty and not required.empty:
            dependent_index = dependent.index[0]
            required_index = required.index[0]

            sections.loc[dependent_index, "scheduled_date"] = "2026-09-01"
            sections.loc[required_index, "scheduled_date"] = "2026-10-01"

            ground_truth.append({
                "anomaly_id": "ANM-004",
                "issue_type": "PREREQUISITE_ORDER_VIOLATION",
                "entity": "Section",
                "record_id": sections.loc[
                    dependent_index, "section_id"
                ],
                "expected_detection": True,
            })

    # ANM-005: Duplicate a section-faculty assignment.
    if not assignments.empty:
        original = assignments.iloc[0].to_dict()
        record_id = "WLA-2026-900005"

        duplicate = {
            **original,
            "workload_assignment_id": record_id,
        }

        assignments = pd.concat(
            [assignments, pd.DataFrame([duplicate])],
            ignore_index=True,
        )

        ground_truth.append({
            "anomaly_id": "ANM-005",
            "issue_type": "DUPLICATE_SECTION_ASSIGNMENT",
            "entity": "WorkloadAssignment",
            "record_id": record_id,
            "expected_detection": True,
        })

    dataset["Section"] = sections
    dataset["WorkloadAssignment"] = assignments

    return dataset, pd.DataFrame(ground_truth)


def detect_anomalies(dataset):
    """Detect business-rule violations in allocated records."""
    findings = []

    sections = dataset["Section"]
    assignments = dataset["WorkloadAssignment"]
    faculty = dataset["Faculty"]
    skills = dataset["FacultySkill"]
    rooms = dataset["Room"]
    courses = dataset["Course"]
    prerequisites = dataset["Prerequisite"]

    # 1. Faculty skill mismatch.
    qualified_pairs = set(
        zip(skills["faculty_id"], skills["course_id"])
    )
    section_course = sections.set_index("section_id")["course_id"].to_dict()

    for row in assignments.to_dict("records"):
        course_id = section_course.get(row["section_id"])

        if course_id and (
            row["faculty_id"], course_id
        ) not in qualified_pairs:
            findings.append({
                "issue_type": "FACULTY_SKILL_MISMATCH",
                "record_id": row["workload_assignment_id"],
            })

    # 2. Workload exceeded.
    confirmed = assignments[assignments["status"] == "CONFIRMED"]
    totals = confirmed.groupby("faculty_id")["weekly_hours"].sum()
    limits = faculty.set_index("faculty_id")["max_weekly_hours"]

    for faculty_id, total in totals.items():
        if faculty_id in limits and total > limits[faculty_id]:
            findings.append({
                "issue_type": "WORKLOAD_EXCEEDED",
                "record_id": faculty_id,
            })

    # 3. Capacity too low relative to target enrollment and room limits.
    room_limits = rooms.set_index("room_id")["capacity"]

    course_targets = courses.set_index("course_id")["target_section_size"]

    for row in sections.to_dict("records"):

        room_capacity = room_limits.get(row["room_id"])

        target_size = course_targets.get(row["course_id"])

        if room_capacity is None or target_size is None:

            continue

        expected_capacity = min(

            int(room_capacity),

            int(target_size),

        )

        if int(row["capacity"]) < expected_capacity:

            findings.append({

                "issue_type": "SECTION_CAPACITY_EXCEEDED",

                "record_id": row["section_id"],

            })

    # 4. Prerequisite ordering; compare every pair of sections.
    sections_by_course = {
        course_id: group
        for course_id, group in sections.groupby("course_id")
    }

    for row in prerequisites.to_dict("records"):
        dependent = sections_by_course.get(row["course_id"])
        required = sections_by_course.get(row["required_course_id"])

        if dependent is None or required is None:
            continue

        dependent_dates = pd.to_datetime(
            dependent["scheduled_date"], errors="coerce"
        )
        required_dates = pd.to_datetime(
            required["scheduled_date"], errors="coerce"
        )

        if (
            not dependent_dates.isna().all()
            and not required_dates.isna().all()
            and dependent_dates.min() < required_dates.min()
        ):
            findings.append({
                "issue_type": "PREREQUISITE_ORDER_VIOLATION",
                "record_id": row["course_id"],
            })

    # 5. Duplicate section-faculty assignments.
    duplicate_mask = assignments.duplicated(
        subset=["section_id", "faculty_id"],
        keep="first",
    )

    for row in assignments.loc[duplicate_mask].to_dict("records"):
        findings.append({
            "issue_type": "DUPLICATE_SECTION_ASSIGNMENT",
            "record_id": row["workload_assignment_id"],
        })

    return pd.DataFrame(findings, columns=["issue_type", "record_id"])
