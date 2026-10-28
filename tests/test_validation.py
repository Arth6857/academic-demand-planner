from src.academic_planner.generator import generate_dataset
from src.academic_planner.validation import validate_dataset


def test_starter_dataset_has_valid_relationships():
    dataset = generate_dataset("starter", seed=20261022)

    assert validate_dataset(dataset) == []


def test_primary_keys_are_unique_and_not_null():
    dataset = generate_dataset("starter", seed=20261022)

    primary_key_columns = {
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

    for entity, dataframe in dataset.items():
        column = primary_key_columns[entity]

        assert column in dataframe.columns, (
            f"Missing primary key column '{column}' in {entity}"
        )

        if not dataframe.empty:
            assert dataframe[column].notna().all(), (
                f"Null primary keys found in {entity}"
            )

            assert dataframe[column].is_unique, (
                f"Duplicate primary keys found in {entity}"
            )