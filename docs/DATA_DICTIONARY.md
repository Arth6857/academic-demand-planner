Academic Demand Planner — Data Dictionary

1. Overview

This document describes the schema of the synthetic academic demand planning dataset. All data is generated synthetically using a configurable random seed. No real student or faculty information is used.

Identifiers are immutable within a generated dataset. Relationships are represented using explicit foreign keys.

2. Program

Primary key: program_id

Field	Type	Required	Allowed values / validation
program_id	String	Yes	Unique; format PRG-000001
program_name	String	Yes	Non-empty
degree_level	String	Yes	UG, PG
department	String	Yes	Non-empty
status	String	Yes	ACTIVE, INACTIVE
effective_date	Date	Yes	ISO format YYYY-MM-DD

Cardinality: One program can contain many courses and student plans.

3. Course

Primary key: course_id

Foreign key: program_id → Program.program_id

Field	Type	Required	Allowed values / validation
course_id	String	Yes	Unique; format CRS-000001
program_id	String	Yes	Must reference an existing program
course_name	String	Yes	Non-empty
category	String	Yes	CORE, ELECTIVE, POPULAR_ELECTIVE, LOW_ENROLLMENT
credits	Integer	Yes	Greater than or equal to 1
target_section_size	Integer	Yes	Greater than or equal to 1
status	String	Yes	ACTIVE, INACTIVE
effective_date	Date	Yes	Valid ISO date

Cardinality: One program has many courses. One course can have many sections.

4. Prerequisite

Primary key: prerequisite_id

Foreign keys:

* course_id → Course.course_id
* required_course_id → Course.course_id

Field	Type	Required	Allowed values / validation
prerequisite_id	String	Yes	Unique
course_id	String	Yes	Existing course
required_course_id	String	Yes	Existing course; cannot equal course_id
minimum_grade	String	Yes	Synthetic grade threshold
effective_date	Date	Yes	Valid ISO date

Cardinality: Courses have a many-to-many prerequisite relationship through this entity.

5. StudentPlan

Primary key: student_plan_id

Foreign key: program_id → Program.program_id

Field	Type	Required	Allowed values / validation
student_plan_id	String	Yes	Unique
program_id	String	Yes	Existing program
student_ref	String	Yes	Unique synthetic student reference
academic_level	Integer	Yes	1–4
plan_status	String	Yes	ACTIVE, INACTIVE
effective_date	Date	Yes	Valid ISO date

Cardinality: One program has many student plans. One student plan can have many registration-interest records.

6. RegistrationInterest

Primary key: interest_id

Foreign keys:

* student_plan_id → StudentPlan.student_plan_id
* course_id → Course.course_id

Field	Type	Required	Allowed values / validation
interest_id	String	Yes	Unique
student_plan_id	String	Yes	Existing student plan
course_id	String	Yes	Existing course
term	String	Yes	Academic period identifier
status	String	Yes	INTERESTED, REGISTERED, WAITLISTED, DROPPED
recorded_date	Date	Yes	Valid ISO date

Cardinality: Student plans and courses have a many-to-many relationship through registration interest.

Business rule: A student plan may have at most one interest record for a particular course and term in the baseline dataset.

7. Faculty

Primary key: faculty_id

Field	Type	Required	Allowed values / validation
faculty_id	String	Yes	Unique; format FAC-000001
faculty_name	String	Yes	Synthetic non-empty name
max_weekly_hours	Integer	Yes	Greater than zero
employment_status	String	Yes	ACTIVE, INACTIVE
effective_date	Date	Yes	Valid ISO date

Cardinality: One faculty member can have many skill and availability records.

8. FacultySkill

Primary key: faculty_skill_id

Foreign keys:

* faculty_id → Faculty.faculty_id
* course_id → Course.course_id

Field	Type	Required	Allowed values / validation
faculty_skill_id	String	Yes	Unique
faculty_id	String	Yes	Existing faculty
course_id	String	Yes	Existing course
skill_level	String	Yes	INTERMEDIATE, ADVANCED
effective_date	Date	Yes	Valid ISO date

Cardinality: Faculty and courses have a many-to-many relationship through FacultySkill.

9. Availability

Primary key: availability_id

Foreign key: faculty_id → Faculty.faculty_id

Field	Type	Required	Allowed values / validation
availability_id	String	Yes	Unique
faculty_id	String	Yes	Existing faculty
term	String	Yes	Academic period identifier
available_hours	Integer	Yes	Zero or greater
on_leave	Boolean	Yes	True or False
effective_from	Date	Yes	Valid ISO date
effective_to	Date	Yes	On or after effective_from

Cardinality: One faculty member can have multiple availability periods.

10. Section

Primary key: section_id

Foreign keys:

* course_id → Course.course_id
* room_id → Room.room_id

Field	Type	Required	Allowed values / validation
section_id	String	Yes	Unique; SEC-2026-000001
course_id	String	Yes	Existing course
room_id	String	Yes	Existing room
term	String	Yes	Academic period identifier
capacity	Integer	Yes	Positive; cannot exceed room capacity
scheduled_date	Date	Yes	Valid date; must respect prerequisites
status	String	Yes	PROPOSED, SCHEDULED, CANCELLED

Cardinality: One course can have multiple sections. One room can host multiple sections at different times.

11. Room

Primary key: room_id

Field	Type	Required	Allowed values / validation
room_id	String	Yes	Unique
room_name	String	Yes	Non-empty
capacity	Integer	Yes	Greater than zero
room_type	String	Yes	LECTURE, LAB, SEMINAR
status	String	Yes	ACTIVE, INACTIVE

Cardinality: One room can accommodate many sections over time.

12. WorkloadAssignment

Primary key: workload_assignment_id

Foreign keys:

* section_id → Section.section_id
* faculty_id → Faculty.faculty_id

Field	Type	Required	Allowed values / validation
workload_assignment_id	String	Yes	Unique; WLA-2026-000001
section_id	String	Yes	Existing section
faculty_id	String	Yes	Existing faculty
weekly_hours	Integer	Yes	Greater than zero
status	String	Yes	PROPOSED, CONFIRMED, CANCELLED
created_at	Timestamp	Yes	Valid timestamp

Cardinality: Faculty members and sections are connected through workload assignments. Assignment history must be retained.

13. Lifecycle and History

Baseline entities use explicit status fields. Material changes to sections and workload assignments should be represented through event records rather than destructive overwrites.

The final implementation will include an event history recording the entity, event type, timestamp, and relevant state transition.

14. Ground Truth

Known anomalies, expected decisions, and evaluation labels must be stored separately from the input features. Each injected anomaly must have an explicit issue type, affected record identifiers, and a documented expected outcome.

Ground truth must not be used as an input feature when calculating forecasts or allocating faculty.