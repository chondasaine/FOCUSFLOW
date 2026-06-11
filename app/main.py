from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import test_database_connection, get_db, engine
import app.models as models
import app.schemas as schemas
import app.crud as crud
from datetime import datetime
from app.analytics import calculate_weekly_summary


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FocusFlow API")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/health/db")
def database_health_check():
    result = test_database_connection()
    return {"database": "connected", "result": result}

# People endpoints
@app.post("/people", response_model=schemas.PersonRead)
def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    return crud.create_person(db=db, person=person)

@app.get("/people", response_model=list[schemas.PersonRead])
def get_people(db: Session = Depends(get_db)):
    return crud.get_people(db=db)

@app.get("/people/{person_id}", response_model=schemas.PersonRead)
def get_person(person_id: int, db: Session = Depends(get_db)):
    person = crud.get_person(db=db, person_id=person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return person

# Project endpoints
@app.post("/projects", response_model=schemas.ProjectRead)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return crud.create_project(db=db, project=project)

@app.get("/projects", response_model=list[schemas.ProjectRead])
def get_projects(db: Session = Depends(get_db)):
    return crud.get_projects(db=db)

@app.get("/projects/{project_id}", response_model=schemas.ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db=db, project_id=project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# project assignment endpoints
@app.post("/project_assignments", response_model=schemas.ProjectAssignmentRead)
def create_project_assignment(project_assignment: schemas.ProjectAssignmentCreate, db: Session = Depends(get_db)):
    return crud.create_project_assignment(db=db, project_assignment=project_assignment)

@app.get("/project_assignments", response_model=list[schemas.ProjectAssignmentRead])
def get_project_assignments(db: Session = Depends(get_db)):
    return crud.get_project_assignments(db=db)

@app.get("/project_assignments/{project_assignment_id}", response_model=schemas.ProjectAssignmentRead)
def get_project_assignment(project_assignment_id: int, db: Session = Depends(get_db)):
    project_assignment = crud.get_project_assignment(db=db, project_assignment_id=project_assignment_id)
    if project_assignment is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_assignment

# Operational Event Endpoints
@app.post("/operational_events", response_model=schemas.OperationalEventRead)
def create_operational_event(operational_event: schemas.OperationalEventCreate, db: Session = Depends(get_db)):
    return crud.create_operational_event(db=db, operational_event=operational_event)

@app.get("/operational_events", response_model=list[schemas.OperationalEventRead])
def get_operational_events(db: Session = Depends(get_db)):
    return crud.get_operational_events(db=db)

@app.get("/operational_events/{operational_event_id}", response_model=schemas.OperationalEventRead)
def get_operational_event(operational_event_id: int, db: Session = Depends(get_db)):
    operational_event = crud.get_operational_event(db=db, operational_event_id=operational_event_id)
    if operational_event is None:
        raise HTTPException(status_code=404, detail="Operational Event not found")
    return operational_event

# Metric Snapshots Endpoints
@app.post("/metric_snapshots", response_model=schemas.MetricSnapshotRead)
def create_metric_snapshot(metric_snapshot: schemas.MetricSnapshotCreate, db: Session = Depends(get_db)):
    return crud.create_metric_snapshot(db=db, metric_snapshot=metric_snapshot)

@app.get("/metric_snapshots", response_model=list[schemas.MetricSnapshotRead])
def get_metric_snapshots(db: Session = Depends(get_db)):
    return crud.get_metric_snapshots(db=db)

@app.get("/metric_snapshots/{metric_snapshot_id}", response_model=schemas.MetricSnapshotRead)
def get_metric_snapshot(metric_snapshot_id: int, db: Session = Depends(get_db)):
    metric_snapshot = crud.get_metric_snapshot(db=db, metric_snapshot_id=metric_snapshot_id)
    if metric_snapshot is None:
        raise HTTPException(status_code=404, detail="Metric Snapshots are not found")
    return metric_snapshot

@app.get("/people/{person_id}/weekly_summary")
def get_weekly_summary(person_id: int, week_start: datetime, db: Session = Depends(get_db)):
    result = calculate_weekly_summary(db=db, person_id=person_id, week_start=week_start)
    if result is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return result