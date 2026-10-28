"""Reproducible synthetic data generator for academic demand planning."""

import random
from datetime import date, timedelta

import pandas as pd

from .config import ACADEMIC_YEAR, RANDOM_SEED, DATASET_SCALES


def make_id(prefix, number, width=6):
    """Create a deterministic, zero-padded identifier."""
    return f"{prefix}-{number:0{width}d}"


def generate_dataset(scale="starter", seed=RANDOM_SEED):
    """Generate the core academic planning entities.

    Returns:
        dict[str, pandas.DataFrame]: One DataFrame per core entity.
    """
    if scale not in DATASET_SCALES:
        raise ValueError(
            f"Unknown scale {scale!r}. Choose from {list(DATASET_SCALES)}."
        )

    config = DATASET_SCALES[scale]
    rng = random.Random(seed)

    # ---------------------------------------------------------
    # 1. PROGRAM: parent/master entity
    # ---------------------------------------------------------
    programs = []

    for i in range(1, config.num_programs + 1):
        programs.append({
            "program_id": make_id("PRG", i),
            "program_name": f"Academic Program {i:03d}",
            "degree_level": rng.choice(["UG", "PG"]),
            "department": f"Department {(i - 1) % 10 + 1:02d}",
            "status": "ACTIVE",
            "effective_date": "2024-01-01",
        })

    programs_df = pd.DataFrame(programs)
    program_ids = programs_df["program_id"].tolist()

    # ---------------------------------------------------------
    # 2. COURSE: each course belongs to one program
    # ---------------------------------------------------------
    courses = []
    courses_per_program = {program_id: 0 for program_id in program_ids}

    for i in range(1, config.num_courses + 1):
        program_id = program_ids[(i - 1) % len(program_ids)]
        courses_per_program[program_id] += 1

        category = rng.choices(
            ["CORE", "ELECTIVE", "POPULAR_ELECTIVE", "LOW_ENROLLMENT"],
            weights=[45, 25, 20, 10],
            k=1,
        )[0]

        courses.append({
            "course_id": make_id("CRS", i),
            "program_id": program_id,
            "course_name": f"Course {i:04d}",
            "category": category,
            "credits": rng.choice([2, 3, 4]),
            "target_section_size": rng.choice([25, 30, 35, 40]),
            "status": "ACTIVE",
            "effective_date": "2024-01-01",
        })

    courses_df = pd.DataFrame(courses)
    course_ids = courses_df["course_id"].tolist()

    # ---------------------------------------------------------
    # 3. PREREQUISITE: directed relationships between courses
    # ---------------------------------------------------------
    prerequisites = []
    prerequisite_number = 1

    # Only earlier course IDs can be prerequisites.
    # This construction prevents prerequisite cycles.
    for i in range(1, len(course_ids)):
        if rng.random() < 0.15:
            prerequisite_id = course_ids[i - 1]
            course_id = course_ids[i]

            prerequisites.append({
                "prerequisite_id": make_id("PRE", prerequisite_number),
                "course_id": course_id,
                "required_course_id": prerequisite_id,
                "minimum_grade": "C",
                "effective_date": "2024-01-01",
            })
            prerequisite_number += 1

    prerequisites_df = pd.DataFrame(
        prerequisites,
        columns=[
            "prerequisite_id",
            "course_id",
            "required_course_id",
            "minimum_grade",
            "effective_date",
        ],
    )

    # ---------------------------------------------------------
    # 4. STUDENT PLAN
    # ---------------------------------------------------------
    student_plans = []

    for i in range(1, config.num_student_plans + 1):
        program_id = rng.choice(program_ids)

        student_plans.append({
            "student_plan_id": make_id("STP", i),
            "program_id": program_id,
            "student_ref": make_id("STU", i),
            "academic_level": rng.randint(1, 4),
            "plan_status": "ACTIVE",
            "effective_date": "2026-01-01",
        })

    student_plans_df = pd.DataFrame(student_plans)

    # ---------------------------------------------------------
    # 5. REGISTRATION INTEREST
    # ---------------------------------------------------------
    # Four historical periods plus the target period.
    # Each student has a unique course per period.
    periods = ["2024FA", "2025SP", "2025FA", "2026SP", "2026FA"]
    interest_records = []
    interest_number = 1

    for student in student_plans:
        program_id = student["program_id"]

        eligible_courses = courses_df.loc[
            courses_df["program_id"] == program_id,
            "course_id",
        ].tolist()

        # Allow some cross-program elective interests.
        if not eligible_courses:
            eligible_courses = course_ids

        selected_count = min(
            len(eligible_courses),
            rng.randint(1, min(4, max(1, len(eligible_courses)))),
        )

        for period in periods:
            selected_courses = rng.sample(
                eligible_courses,
                k=selected_count,
            )

            for course_id in selected_courses:
                status = rng.choices(
                    ["INTERESTED", "REGISTERED", "WAITLISTED", "DROPPED"],
                    weights=[25, 55, 12, 8],
                    k=1,
                )[0]

                interest_records.append({
                    "interest_id": make_id("INT", interest_number),
                    "student_plan_id": student["student_plan_id"],
                    "course_id": course_id,
                    "term": period,
                    "status": status,
                    "recorded_date": {
                        "2024FA": "2024-08-01",
                        "2025SP": "2025-01-01",
                        "2025FA": "2025-08-01",
                        "2026SP": "2026-01-01",
                        "2026FA": "2026-08-01",
                    }[period],
                })
                interest_number += 1

    registration_interest_df = pd.DataFrame(interest_records)

    # ---------------------------------------------------------
    # 6. FACULTY
    # ---------------------------------------------------------
    faculty = []

    for i in range(1, config.num_faculty + 1):
        faculty.append({
            "faculty_id": make_id("FAC", i),
            "faculty_name": f"Faculty Member {i:04d}",
            "max_weekly_hours": rng.choice([8, 10, 12, 15, 18]),
            "employment_status": "ACTIVE",
            "effective_date": "2026-01-01",
        })

    faculty_df = pd.DataFrame(faculty)
    faculty_ids = faculty_df["faculty_id"].tolist()

    # ---------------------------------------------------------
    # 7. FACULTY SKILL: faculty-course bridge table
    # ---------------------------------------------------------
    faculty_skills = []
    skill_number = 1

    for faculty_member in faculty:
        skill_count = min(3, len(course_ids))
        qualified_courses = rng.sample(course_ids, k=skill_count)

        for course_id in qualified_courses:
            faculty_skills.append({
                "faculty_skill_id": make_id("FSK", skill_number),
                "faculty_id": faculty_member["faculty_id"],
                "course_id": course_id,
                "skill_level": rng.choice(["INTERMEDIATE", "ADVANCED"]),
                "effective_date": "2026-01-01",
            })
            skill_number += 1

    faculty_skills_df = pd.DataFrame(faculty_skills)

    # ---------------------------------------------------------
    # 8. AVAILABILITY
    # ---------------------------------------------------------
    availability = []

    for i, faculty_member in enumerate(faculty, start=1):
        # A small, deterministic proportion of faculty are on leave.
        on_leave = rng.random() < 0.05

        availability.append({
            "availability_id": make_id("AVL", i),
            "faculty_id": faculty_member["faculty_id"],
            "term": "2026FA",
            "available_hours": (
                0 if on_leave else faculty_member["max_weekly_hours"]
            ),
            "on_leave": on_leave,
            "effective_from": "2026-08-01",
            "effective_to": "2026-12-31",
        })

    availability_df = pd.DataFrame(availability)

    # ---------------------------------------------------------
    # 9. ROOM
    # ---------------------------------------------------------
    rooms = []

    room_count = max(5, min(200, config.num_courses // 2))

    for i in range(1, room_count + 1):
        rooms.append({
            "room_id": make_id("ROM", i),
            "room_name": f"Room {i:03d}",
            "capacity": rng.choice([20, 25, 30, 35, 40, 50, 60]),
            "room_type": rng.choice(["LECTURE", "LAB", "SEMINAR"]),
            "status": "ACTIVE",
        })

    rooms_df = pd.DataFrame(rooms)

    # ---------------------------------------------------------
    # 10. SECTION: initially empty; populated by the allocator
    # ---------------------------------------------------------
    sections_df = pd.DataFrame(columns=[
        "section_id",
        "course_id",
        "room_id",
        "term",
        "capacity",
        "scheduled_date",
        "status",
    ])

    # ---------------------------------------------------------
    # 11. WORKLOAD ASSIGNMENT: initially empty
    # ---------------------------------------------------------
    workload_assignments_df = pd.DataFrame(columns=[
        "workload_assignment_id",
        "section_id",
        "faculty_id",
        "weekly_hours",
        "status",
        "created_at",
    ])

    # ---------------------------------------------------------
    # Return all required core entities.
    # ---------------------------------------------------------
    return {
        "Program": programs_df,
        "Course": courses_df,
        "Prerequisite": prerequisites_df,
        "StudentPlan": student_plans_df,
        "RegistrationInterest": registration_interest_df,
        "Faculty": faculty_df,
        "FacultySkill": faculty_skills_df,
        "Availability": availability_df,
        "Section": sections_df,
        "Room": rooms_df,
        "WorkloadAssignment": workload_assignments_df,
    }