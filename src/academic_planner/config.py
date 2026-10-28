"""Configuration for the academic demand planning system."""

from dataclasses import dataclass


RANDOM_SEED = 20261022
ACADEMIC_YEAR = 2026


@dataclass(frozen=True)
class DatasetConfig:
    """Controls the size of the synthetic dataset."""

    num_programs: int
    num_courses: int
    num_faculty: int
    num_student_plans: int
    scale_name: str


DATASET_SCALES = {
    "starter": DatasetConfig(
        num_programs=5,
        num_courses=30,
        num_faculty=15,
        num_student_plans=200,
        scale_name="starter",
    ),
    "full": DatasetConfig(
        num_programs=100,
        num_courses=1000,
        num_faculty=500,
        num_student_plans=20000,
        scale_name="full",
    ),
}