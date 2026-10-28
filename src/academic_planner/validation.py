import pandas as pd


PRIMARY_KEYS = {
    "Program": "program_id",
    "Course": "course_id",
    "Prerequisite": "prerequisite_id",
    "StudentPlan": "student_plan_id",
    "RegistrationInterest": "interest_id",
    "Faculty": "faculty_id",
    "FacultySkill": "faculty_skill_id",
    "Availability": "availability_id",
    "Section": "section_id",
    "Room": "room_id",
    "WorkloadAssignment": "workload_assignment_id",
}


FOREIGN_KEYS = {
    "Course": {
        "program_id": ("Program", "program_id"),
    },
    "Prerequisite": {
        "course_id": ("Course", "course_id"),
        "required_course_id": ("Course", "course_id"),
    },
    "StudentPlan": {
        "program_id": ("Program", "program_id"),
    },
    "RegistrationInterest": {
        "student_plan_id": ("StudentPlan", "student_plan_id"),
        "course_id": ("Course", "course_id"),
    },
    "FacultySkill": {
        "faculty_id": ("Faculty", "faculty_id"),
        "course_id": ("Course", "course_id"),
    },
    "Availability": {
        "faculty_id": ("Faculty", "faculty_id"),
    },
    "Section": {
        "course_id": ("Course", "course_id"),
        "room_id": ("Room", "room_id"),
    },
    "WorkloadAssignment": {
        "section_id": ("Section", "section_id"),
        "faculty_id": ("Faculty", "faculty_id"),
    },
}


ALLOWED_VALUES = {
    "Program": {
        "degree_level": {"UG", "PG"},
        "status": {"ACTIVE", "INACTIVE"},
    },
    "Course": {
        "category": {
            "CORE",
            "ELECTIVE",
            "POPULAR_ELECTIVE",
            "LOW_ENROLLMENT",
        },
        "status": {"ACTIVE", "INACTIVE"},
    },
    "RegistrationInterest": {
        "status": {
            "INTERESTED",
            "REGISTERED",
            "WAITLISTED",
            "DROPPED",
        },
    },
    "Faculty": {
        "employment_status": {"ACTIVE", "INACTIVE"},
    },
    "FacultySkill": {
        "skill_level": {"INTERMEDIATE", "ADVANCED"},
    },
    "Section": {
        "status": {"PROPOSED", "SCHEDULED", "CANCELLED"},
    },
    "WorkloadAssignment": {
        "status": {"PROPOSED", "CONFIRMED", "CANCELLED"},
    },
}


def validate_dataset(dataset):
    """Return a list of integrity issues in a generated dataset.

    An empty list means all implemented checks passed.
    """
    issues = []

    def add_issue(entity, check, message, count=1):
        issues.append({
            "entity": entity,
            "check": check,
            "message": message,
            "records_affected": int(count),
        })

    # --------------------------------------------------
    # 1. Required entities and primary keys
    # --------------------------------------------------
    for entity, pk in PRIMARY_KEYS.items():
        if entity not in dataset:
            add_issue(entity, "MISSING_ENTITY", "Entity is missing.")
            continue

        df = dataset[entity]

        if pk not in df.columns:
            add_issue(entity, "MISSING_PRIMARY_KEY", f"Missing column: {pk}")
            continue

        if df[pk].isna().any():
            add_issue(
                entity,
                "NULL_PRIMARY_KEY",
                f"{pk} contains null values.",
                df[pk].isna().sum(),
            )

        duplicate_mask = df[pk].duplicated(keep=False)

        if duplicate_mask.any():
            add_issue(
                entity,
                "DUPLICATE_PRIMARY_KEY",
                f"{pk} contains duplicate values.",
                duplicate_mask.sum(),
            )

    # --------------------------------------------------
    # 2. Foreign-key integrity
    # --------------------------------------------------
    for entity, relationships in FOREIGN_KEYS.items():
        if entity not in dataset:
            continue

        child = dataset[entity]

        for fk, (parent_entity, parent_pk) in relationships.items():
            if fk not in child.columns:
                add_issue(
                    entity,
                    "MISSING_FOREIGN_KEY",
                    f"Missing column: {fk}",
                )
                continue

            if parent_entity not in dataset:
                continue

            parent = dataset[parent_entity]

            if parent_pk not in parent.columns:
                continue

            non_null_values = child[fk].dropna()

            invalid_mask = ~non_null_values.isin(parent[parent_pk])

            if invalid_mask.any():
                add_issue(
                    entity,
                    "INVALID_FOREIGN_KEY",
                    f"{fk} references missing {parent_entity} records.",
                    invalid_mask.sum(),
                )

    # --------------------------------------------------
    # 3. Allowed categorical values
    # --------------------------------------------------
    for entity, columns in ALLOWED_VALUES.items():
        if entity not in dataset:
            continue

        df = dataset[entity]

        for column, allowed in columns.items():
            if column not in df.columns:
                continue

            invalid = df[column].notna() & ~df[column].isin(allowed)

            if invalid.any():
                add_issue(
                    entity,
                    "INVALID_ENUM",
                    f"{column} contains unsupported values.",
                    invalid.sum(),
                )

    # --------------------------------------------------
    # 4. Duplicate business relationships
    # --------------------------------------------------
    relationship_keys = {
        "Prerequisite": ["course_id", "required_course_id"],
        "FacultySkill": ["faculty_id", "course_id"],
        "RegistrationInterest": [
            "student_plan_id",
            "course_id",
            "term",
        ],
        "Availability": ["faculty_id", "term"],
        "WorkloadAssignment": ["section_id", "faculty_id"],
    }

    for entity, columns in relationship_keys.items():
        if entity not in dataset:
            continue

        df = dataset[entity]

        if not all(column in df.columns for column in columns):
            continue

        duplicate_mask = df.duplicated(subset=columns, keep=False)

        if duplicate_mask.any():
            add_issue(
                entity,
                "DUPLICATE_RELATIONSHIP",
                f"Duplicate relationship across {columns}.",
                duplicate_mask.sum(),
            )

    # --------------------------------------------------
    # 5. Prerequisite rules
    # --------------------------------------------------
    if "Prerequisite" in dataset:
        prerequisites = dataset["Prerequisite"]

        if {
            "course_id",
            "required_course_id",
        }.issubset(prerequisites.columns):

            self_reference = (
                prerequisites["course_id"]
                == prerequisites["required_course_id"]
            )

            if self_reference.any():
                add_issue(
                    "Prerequisite",
                    "SELF_PREREQUISITE",
                    "A course cannot be its own prerequisite.",
                    self_reference.sum(),
                )

    # --------------------------------------------------
    # 6. Numeric capacity and workload checks
    # --------------------------------------------------
    numeric_rules = {
        "Course": {
            "credits": 1,
            "target_section_size": 1,
        },
        "Faculty": {
            "max_weekly_hours": 0,
        },
        "Room": {
            "capacity": 0,
        },
        "Availability": {
            "available_hours": 0,
        },
        "Section": {
            "capacity": 1,
        },
        "WorkloadAssignment": {
            "weekly_hours": 0,
        },
    }

    for entity, columns in numeric_rules.items():
        if entity not in dataset:
            continue

        df = dataset[entity]

        for column, minimum in columns.items():
            if column not in df.columns:
                continue

            values = pd.to_numeric(df[column], errors="coerce")

            invalid = (
                values.isna()
                | (values < minimum)
            )

            if invalid.any():
                add_issue(
                    entity,
                    "INVALID_NUMERIC_VALUE",
                    f"{column} must be numeric and at least {minimum}.",
                    invalid.sum(),
                )

    # --------------------------------------------------
    # 7. Date ordering for availability records
    # --------------------------------------------------
    if "Availability" in dataset:
        availability = dataset["Availability"]

        if {"effective_from", "effective_to"}.issubset(
            availability.columns
        ):
            start = pd.to_datetime(
                availability["effective_from"],
                errors="coerce",
            )
            end = pd.to_datetime(
                availability["effective_to"],
                errors="coerce",
            )

            invalid = start.isna() | end.isna() | (start > end)

            if invalid.any():
                add_issue(
                    "Availability",
                    "INVALID_DATE_RANGE",
                    "Availability dates are invalid or reversed.",
                    invalid.sum(),
                )

    return issues


def validation_report(dataset):
    """Return validation results as a pandas DataFrame."""
    issues = validate_dataset(dataset)

    columns = [
        "entity",
        "check",
        "message",
        "records_affected",
    ]

    return pd.DataFrame(issues, columns=columns)


def assert_valid_dataset(dataset):
    """Raise an error if any integrity checks fail."""
    report = validation_report(dataset)

    if not report.empty:
        raise ValueError(
            "Dataset validation failed:\n"
            + report.to_string(index=False)
        )

    return True