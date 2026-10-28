from pandas.testing import assert_frame_equal

from src.academic_planner.generator import generate_dataset


def test_generator_returns_all_required_entities():
    dataset = generate_dataset("starter", seed=20261022)

    expected_entities = {
        "Program",
        "Course",
        "Prerequisite",
        "StudentPlan",
        "RegistrationInterest",
        "Faculty",
        "FacultySkill",
        "Availability",
        "Section",
        "Room",
        "WorkloadAssignment",
    }

    assert set(dataset.keys()) == expected_entities


def test_generator_is_deterministic():
    dataset_1 = generate_dataset("starter", seed=20261022)
    dataset_2 = generate_dataset("starter", seed=20261022)

    for entity in dataset_1:
        assert_frame_equal(dataset_1[entity], dataset_2[entity])


def test_generator_creates_expected_starter_scale():
    dataset = generate_dataset("starter", seed=20261022)

    assert len(dataset["Program"]) == 5
    assert len(dataset["Course"]) == 30
    assert len(dataset["Faculty"]) == 15
    assert len(dataset["StudentPlan"]) == 200