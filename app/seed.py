import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import random
import pytz
from app.database import SessionLocal
from app.models import(
    Person, Project, ProjectAssignment,
    OperationalEvent, MetricSnapshots, 
    EventType, EventSource
)
from app.analytics import calculate_weekly_summary

# Delete Data in Order of Dependency from DB

EST = pytz.timezone("US/Eastern")

def clear_data(db):
    print("Clearing existing data...")
    db.query(MetricSnapshots).delete()
    db.query(OperationalEvent).delete()
    db.query(ProjectAssignment).delete()
    db.query(Project).delete()
    db.query(Person).delete()
    db.commit()
    print("Data cleared.")

# Create & Commit People to DB

def create_people(db):
    print("Creating people...")
    people = [
        Person(
            name="Chonda Saine",
            email="chonda@company.com",
            role="Client Relations Manager and Bloomfire Product Lead",
            weekly_capacity_hours=40.0
        ),
        Person(
            name="Sondra Williams",
            email="sondra@company.com",
            role="HR Manager and Bloomfire Implementation Specialist",
            weekly_capacity_hours=40.0
        ),
        Person(
            name="Collin Warner",
            email="collin@company.com",
            role="Foundation Product Lead",
            weekly_capacity_hours=40.0
        ),
        Person(
            name="Will Segal",
            email="will@company.com",
            role="Foundation Implementation Specialist",
            weekly_capacity_hours=40.0
        ),
        Person(
            name="Matt Barnes",
            email="matt@company.com",
            role="Technical Lead",
            weekly_capacity_hours=40.0
        ),
        Person(
            name="Gabriel Leads",
            email="gabriel@company.com",
            role="PMO and Foundation Consultant",
            weekly_capacity_hours=40.0
        ),
    ]
    for person in people:
        db.add(person)
    db.commit()
    for person in people:
        db.refresh(person)
    print(f"{len(people)} people created.")
    return people

# Create & Commit Projects and Assignments to DB

def create_projects_and_assignments(db, people):
    print("Creating projects...")
    projects = [
        Project(
            name="Bloomfire Implementation",
            client_name="Apex Dynamics Corp",
            status="active"
        ),
        Project(
            name="Foundation Implementation",
            client_name="Meridian Solutions Group",
            status="active"
        ),
        Project(
            name="Foundation Implementation",
            client_name="Crestview Enterprises",
            status="active"
        ),
        Project(
            name="Bloomfire Implementation",
            client_name="Pinnacle Global Inc",
            status="active"
        ),
    ]
    for project in projects:
        db.add(project)
    db.commit()
    for project in projects:
        db.refresh(project)
    print(f"{len(projects)} projects created.")

    print("Creating assignments...")
    assignments = [
        ProjectAssignment(person_id=people[0].id, project_id=projects[0].id, expected_hours=15.0),
        ProjectAssignment(person_id=people[0].id, project_id=projects[3].id, expected_hours=10.0),
        ProjectAssignment(person_id=people[1].id, project_id=projects[0].id, expected_hours=20.0),
        ProjectAssignment(person_id=people[1].id, project_id=projects[3].id, expected_hours=15.0),
        ProjectAssignment(person_id=people[2].id, project_id=projects[1].id, expected_hours=20.0),
        ProjectAssignment(person_id=people[2].id, project_id=projects[2].id, expected_hours=15.0),
        ProjectAssignment(person_id=people[3].id, project_id=projects[1].id, expected_hours=25.0),
        ProjectAssignment(person_id=people[3].id, project_id=projects[2].id, expected_hours=20.0),
        ProjectAssignment(person_id=people[4].id, project_id=projects[0].id, expected_hours=10.0),
        ProjectAssignment(person_id=people[4].id, project_id=projects[1].id, expected_hours=10.0),
        ProjectAssignment(person_id=people[4].id, project_id=projects[2].id, expected_hours=10.0),
        ProjectAssignment(person_id=people[4].id, project_id=projects[3].id, expected_hours=10.0),
        ProjectAssignment(person_id=people[5].id, project_id=projects[1].id, expected_hours=20.0),
        ProjectAssignment(person_id=people[5].id, project_id=projects[2].id, expected_hours=15.0),
    ]
    for assignment in assignments:
        db.add(assignment)
    db.commit()
    print(f"{len(assignments)} assignments created.")
    return projects

# Generate Operational Events for Each Person for Each Week

def generate_events(db, people, projects, week_start, week_number):
    print(f"Generating events for week {week_number}...")
    events = []

    # Week profiles — how many of each event type per person per week
    # Format: (meetings, emails, interruptions, direct_messages)
    # Week 1 = baseline, Week 2 = trouble starts,
    # Week 3 = crisis, Week 4 = stabilising

    profiles = {
        "chonda": [
            (8, 25, 5, 8),   # Week 1 — busy but manageable
            (12, 45, 10, 15), # Week 2 — project trouble starts
            (18, 70, 18, 25), # Week 3 — full crisis
            (14, 55, 12, 18), # Week 4 — stabilising
        ],
        "sondra": [
            (6, 20, 3, 5),
            (8, 35, 6, 10),
            (12, 55, 10, 15),
            (9, 40, 7, 10),
        ],
        "collin": [
            (7, 18, 4, 6),
            (9, 28, 6, 8),
            (11, 40, 8, 12),
            (9, 30, 6, 8),
        ],
        "will": [
            (5, 15, 3, 4),
            (8, 25, 8, 10),
            (14, 45, 14, 18),
            (11, 35, 10, 12),
        ],
        "matt": [
            (4, 20, 8, 10),
            (6, 30, 12, 15),
            (10, 50, 18, 20),
            (8, 38, 12, 14),
        ],
        "gabriel": [
            (9, 22, 5, 7),
            (12, 35, 8, 12),
            (16, 55, 12, 18),
            (12, 42, 9, 13),
        ],
    }

    person_keys = ["chonda", "sondra", "collin", "will", "matt", "gabriel"]
    week_idx = week_number - 1

    for i, person in enumerate(people):
        key = person_keys[i]
        meeting_count, email_count, interruption_count, dm_count = profiles[key][week_idx]

        # Adjust capacity for crisis weeks
        if week_number in [2, 3] and key in ["chonda", "will", "matt", "gabriel"]:
            person.weekly_capacity_hours = 50.0 if week_number == 2 else 60.0
            db.commit()

        # Generate meetings
        for m in range(meeting_count):
            day_offset = random.randint(0, 6)
            hour = random.randint(8, 16)
            started_at = EST.localize(
                week_start + timedelta(days=day_offset, hours=hour)
            )
            events.append(OperationalEvent(
                person_id=person.id,
                project_id=random.choice(projects).id,
                source=EventSource.outlook,
                event_type=EventType.meeting,
                duration_minutes=random.choice([30, 45, 60, 90, 120]),
                started_at=started_at
            ))

        # Generate emails
        for e in range(email_count):
            day_offset = random.randint(0, 6)
            hour = random.randint(7, 21)
            started_at = EST.localize(
                week_start + timedelta(days=day_offset, hours=hour)
            )
            events.append(OperationalEvent(
                person_id=person.id,
                project_id=random.choice(projects).id,
                source=EventSource.outlook,
                event_type=EventType.email,
                duration_minutes=random.randint(2, 15),
                started_at=started_at
            ))

        # Generate interruptions
        for r in range(interruption_count):
            day_offset = random.randint(0, 6)
            hour = random.randint(8, 18)
            started_at = EST.localize(
                week_start + timedelta(days=day_offset, hours=hour)
            )
            events.append(OperationalEvent(
                person_id=person.id,
                project_id=random.choice(projects).id,
                source=random.choice([EventSource.teams, EventSource.slack]),
                event_type=EventType.interruption,
                duration_minutes=random.randint(5, 20),
                started_at=started_at
            ))

        # Generate direct messages
        for d in range(dm_count):
            day_offset = random.randint(0, 6)
            hour = random.randint(7, 22)
            started_at = EST.localize(
                week_start + timedelta(days=day_offset, hours=hour)
            )
            events.append(OperationalEvent(
                person_id=person.id,
                project_id=random.choice(projects).id,
                source=random.choice([EventSource.teams, EventSource.slack]),
                event_type=EventType.direct_message,
                duration_minutes=random.randint(2, 10),
                started_at=started_at
            ))

    for event in events:
        db.add(event)
    db.commit()
    print(f"{len(events)} events created for week {week_number}.")

# Calculate Weekly Summaries for All People

def calculate_summaries(db, people, week_starts):
    print("Calculating weekly summaries...")

    # capacity per person per week
    # people list order: chonda, sondra, collin, will, matt, gabriel
    capacity_by_week = [
        [40.0, 40.0, 40.0, 40.0, 40.0, 40.0],  # Week 1 — baseline
        [50.0, 40.0, 40.0, 50.0, 50.0, 40.0],  # Week 2 — trouble starts
        [60.0, 40.0, 40.0, 60.0, 60.0, 40.0],  # Week 3 — crisis
        [40.0, 40.0, 40.0, 40.0, 40.0, 40.0],  # Week 4 — stabilising
    ]

    for week_idx, week_start in enumerate(week_starts):
        for person_idx, person in enumerate(people):
            capacity = capacity_by_week[week_idx][person_idx]
            calculate_weekly_summary(
                db=db,
                person_id=person.id,
                week_start=week_start,
                capacity_hours=capacity
            )
    print("Weekly summaries calculated.")


# Main Runner

def seed():
    db = SessionLocal()
    try:
        clear_data(db)

        people = create_people(db)
        projects = create_projects_and_assignments(db, people)

        week_starts = [
            datetime(2026, 5, 18),  # Week 1 — baseline
            datetime(2026, 5, 25),  # Week 2 — trouble starts
            datetime(2026, 6, 1),   # Week 3 — crisis
            datetime(2026, 6, 8),   # Week 4 — stabilising
        ]

        for i, week_start in enumerate(week_starts):
            generate_events(db, people, projects, week_start, i + 1)

        calculate_summaries(db, people, week_starts)

        print("Seed complete.")

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()