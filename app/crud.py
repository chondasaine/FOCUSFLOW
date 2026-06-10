from sqlalchemy.orm import Session
from app.models import Person, Project, ProjectAssignment, OperationalEvent, MetricSnapshots
from app.schemas import PersonCreate, ProjectCreate, ProjectAssignmentCreate, OperationalEventCreate, MetricSnapshotCreate

def create_person(db: Session, person: PersonCreate):
    db_person = Person(
        name=person.name,
        email=person.email,
        role=person.role,
        weekly_capacity_hours=person.weekly_capacity_hours
    )
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

def get_people(db: Session):
    return db.query(Person).all()

def get_person(db: Session, person_id: int):
    return db.query(Person).filter(Person.id == person_id).first()

def create_project(db: Session, project: ProjectCreate):
    db_project = Project(
        name=project.name,
        client_name=project.client_name,
        status=project.status
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_projects(db: Session):
    return db.query(Project).all()

def get_project(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()

def create_project_assignment(db: Session, project_assignment: ProjectAssignmentCreate):
    db_project_assignment = ProjectAssignment(
        person_id=project_assignment.person_id,
        project_id=project_assignment.project_id,
        expected_hours=project_assignment.expected_hours
    )
    db.add(db_project_assignment)
    db.commit()
    db.refresh(db_project_assignment)
    return db_project_assignment

def get_project_assignments(db:Session):
    return db.query(ProjectAssignment).all()

def get_project_assignment(db:Session, project_assignment_id: int):
    return db.query(ProjectAssignment).filter(ProjectAssignment.id == project_assignment_id).first()

def create_operational_event(db: Session, operational_event: OperationalEventCreate):
    db_operational_event = OperationalEvent(
        person_id=operational_event.person_id,
        project_id=operational_event.project_id,
        source=operational_event.source,
        event_type=operational_event.event_type,
        duration_minutes=operational_event.duration_minutes,
        event_metadata=operational_event.event_metadata,
        started_at=operational_event.started_at
    )
    db.add(db_operational_event)
    db.commit()
    db.refresh(db_operational_event)
    return db_operational_event

def get_operational_events(db:Session):
    return db.query(OperationalEvent).all()

def get_operational_event(db:Session, operational_event_id: int):
    return db.query(OperationalEvent).filter(OperationalEvent.id == operational_event_id).first()

def create_metric_snapshot(db: Session, metric_snapshot: MetricSnapshotCreate):
    db_metric_snapshot = MetricSnapshots(
        person_id=metric_snapshot.person_id,
        week_start=metric_snapshot.week_start,
        meeting_hours=metric_snapshot.meeting_hours,
        email_count=metric_snapshot.email_count,
        interruption_count=metric_snapshot.interruption_count,
        focus_hours=metric_snapshot.focus_hours,
        fragmentation_score=metric_snapshot.fragmentation_score
    )
    db.add(db_metric_snapshot)
    db.commit()
    db.refresh(db_metric_snapshot)
    return db_metric_snapshot

def get_metric_snapshots(db:Session):
    return db.query(MetricSnapshots).all()

def get_metric_snapshot(db:Session, metric_snapshot_id: int):
    return db.query(MetricSnapshots).filter(MetricSnapshots.id == metric_snapshot_id).first()