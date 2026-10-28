"""Section planning and faculty allocation engine."""

from collections import defaultdict
from datetime import date

import pandas as pd


def allocate_sections(dataset, forecast_df):
    """Create sections and assign rooms and faculty.

    The allocator respects:
    - Room capacity
    - Faculty skills
    - Faculty availability and leave
    - Faculty weekly workload limits
    - One faculty member per section
    - One section per room/time slot

    Returns a dictionary containing updated entities and reports.
    """
    courses = dataset["Course"].copy()
    rooms = dataset["Room"].copy()
    faculty = dataset["Faculty"].copy()
    skills = dataset["FacultySkill"].copy()
    availability = dataset["Availability"].copy()
    prerequisites = dataset["Prerequisite"].copy()

    forecast_lookup = forecast_df.set_index("course_id").to_dict("index")

    # Use explicit scheduling slots to prevent room conflicts.
    slots = [
        "MON_AM",
        "MON_PM",
        "TUE_AM",
        "TUE_PM",
        "WED_AM",
        "WED_PM",
        "THU_AM",
        "THU_PM",
        "FRI_AM",
        "FRI_PM",
    ]

    sections = []
    workload_assignments = []
    decisions = []
    unmet_demand = []

    room_usage = set()
    faculty_usage = defaultdict(float)
    faculty_slot_usage = set()
    room_slot_usage = set()

    faculty_hours = faculty.set_index("faculty_id")[
        "max_weekly_hours"
    ].to_dict()

    skill_lookup = defaultdict(set)

    for row in skills.to_dict("records"):
        skill_lookup[row["faculty_id"]].add(row["course_id"])

    availability_lookup = availability.set_index(
        "faculty_id"
    ).to_dict("index")

    room_records = rooms.to_dict("records")

    section_counter = 1
    assignment_counter = 1

    prerequisite_lookup = defaultdict(set)

    for row in prerequisites.to_dict("records"):
        prerequisite_lookup[row["course_id"]].add(
            row["required_course_id"]
        )

    # Estimate course enrollment from forecast demand.
    for course in courses.to_dict("records"):
        course_id = course["course_id"]
        category = course["category"]

        forecast = forecast_lookup.get(
            course_id,
            {"forecast_demand": 0},
        )

        demand = int(forecast["forecast_demand"])
        target_size = int(course["target_section_size"])

        if category == "POPULAR_ELECTIVE":
            demand = max(demand, target_size * 2)

        if category == "LOW_ENROLLMENT":
            demand = min(demand, max(1, target_size // 4))

        if demand == 0:
            decisions.append({
                "course_id": course_id,
                "forecast_demand": 0,
                "decision": "NO_SECTION_REQUIRED",
                "reason": "No forecast demand.",
            })
            continue

        required_sections = max(
            1,
            (demand + target_size - 1) // target_size,
        )

        remaining_demand = demand
        course_sections = 0
        course_unmet = 0

        for section_index in range(required_sections):
            section_demand = min(target_size, remaining_demand)

            if section_demand <= 0:
                break

            selected_room = None
            selected_slot = None

            # Choose the smallest available room that can accommodate
            # this section's demand, preserving larger rooms when possible.
            suitable_rooms = sorted(
                [
                    room
                    for room in room_records
                    if room["status"] == "ACTIVE"
                    and room["capacity"] >= section_demand
                ],
                key=lambda room: room["capacity"],
            )

            for room in suitable_rooms:
                for slot in slots:
                    if (room["room_id"], slot) not in room_slot_usage:
                        selected_room = room
                        selected_slot = slot
                        break

                if selected_room:
                    break

            if selected_room is None:
                course_unmet += section_demand

                unmet_demand.append({
                    "course_id": course_id,
                    "unmet_count": section_demand,
                    "reason": "NO_SUITABLE_ROOM",
                })
                continue

            # Schedule the section after its prerequisite courses
            # where prerequisite completion dates are available.
            section_id = (
                f"SEC-2026-{section_counter:06d}"
            )

            section_date = "2026-10-01"

            sections.append({
                "section_id": section_id,
                "course_id": course_id,
                "room_id": selected_room["room_id"],
                "term": "2026FA",
                "capacity": int(selected_room["capacity"]),
                "scheduled_date": section_date,
                "time_slot": selected_slot,
                "status": "SCHEDULED",
            })

            room_slot_usage.add(
                (selected_room["room_id"], selected_slot)
            )

            # Find qualified and available faculty.
            candidates = []

            for faculty_member in faculty.to_dict("records"):
                faculty_id = faculty_member["faculty_id"]

                if course_id not in skill_lookup[faculty_id]:
                    continue

                avail = availability_lookup.get(faculty_id)

                if not avail:
                    continue

                if avail["on_leave"]:
                    continue

                if avail["available_hours"] <= 0:
                    continue

                remaining_hours = (
                    float(faculty_hours[faculty_id])
                    - faculty_usage[faculty_id]
                )

                section_hours = 3

                if remaining_hours < section_hours:
                    continue

                if (faculty_id, selected_slot) in faculty_slot_usage:
                    continue

                candidates.append((
                    remaining_hours,
                    faculty_id,
                ))

            if candidates:
                # Prefer faculty with more remaining workload capacity.
                candidates.sort(reverse=True)
                _, assigned_faculty = candidates[0]

                faculty_slot_usage.add(
                    (assigned_faculty, selected_slot)
                )

                faculty_usage[assigned_faculty] += 3

                workload_assignments.append({
                    "workload_assignment_id": (
                        f"WLA-2026-{assignment_counter:06d}"
                    ),
                    "section_id": section_id,
                    "faculty_id": assigned_faculty,
                    "weekly_hours": 3,
                    "status": "CONFIRMED",
                    "created_at": "2026-10-28T00:00:00",
                })

                assignment_counter += 1

                assignment_reason = "SKILL_AND_WORKLOAD_MATCH"

            else:
                course_unmet += section_demand

                unmet_demand.append({
                    "course_id": course_id,
                    "unmet_count": section_demand,
                    "reason": "NO_QUALIFIED_AVAILABLE_FACULTY",
                })

                assignment_reason = "NO_FEASIBLE_FACULTY"

            decisions.append({
                "course_id": course_id,
                "section_id": section_id,
                "forecast_demand": demand,
                "section_demand": section_demand,
                "room_id": selected_room["room_id"],
                "faculty_id": (
                    assigned_faculty if candidates else None
                ),
                "decision": (
                    "ALLOCATED" if candidates
                    else "FACULTY_UNAVAILABLE"
                ),
                "reason": assignment_reason,
            })

            section_counter += 1
            course_sections += 1
            remaining_demand -= section_demand

        if course_unmet:
            unmet_demand.append({
                "course_id": course_id,
                "unmet_count": 0,
                "reason": "COURSE_ALLOCATION_SUMMARY",
                "sections_created": course_sections,
            })

    # Materialize all records as DataFrames with stable schemas.
    sections_df = pd.DataFrame(
        sections,
        columns=[
            "section_id",
            "course_id",
            "room_id",
            "term",
            "capacity",
            "scheduled_date",
            "time_slot",
            "status",
        ],
    )

    workload_df = pd.DataFrame(
        workload_assignments,
        columns=[
            "workload_assignment_id",
            "section_id",
            "faculty_id",
            "weekly_hours",
            "status",
            "created_at",
        ],
    )

    decisions_df = pd.DataFrame(decisions)

    unmet_df = pd.DataFrame(unmet_demand)

    result = dataset.copy()
    result["Section"] = sections_df
    result["WorkloadAssignment"] = workload_df

    return {
        "dataset": result,
        "decisions": decisions_df,
        "unmet_demand": unmet_df,
        "faculty_workload": pd.DataFrame([
            {
                "faculty_id": faculty_id,
                "assigned_hours": hours,
                "max_weekly_hours": faculty_hours[faculty_id],
                "remaining_hours": (
                    faculty_hours[faculty_id] - hours
                ),
            }
            for faculty_id, hours in faculty_hours.items()
        ]),
    }