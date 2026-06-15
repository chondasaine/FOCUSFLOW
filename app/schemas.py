from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Dict, Any
from app.models import EventType, EventSource

class PersonCreate(BaseModel):
    name: str
    email: EmailStr
    role: Optional[str] = None
    weekly_capacity_hours: Optional[float] = 40.0

class PersonRead(PersonCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProjectCreate(BaseModel):
    name: str
    client_name: Optional[str] = None
    status: Optional[str] = "active"

class ProjectRead(ProjectCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProjectAssignmentCreate(BaseModel):
    person_id: int
    project_id: int
    expected_hours: Optional[float] = None

class ProjectAssignmentRead(ProjectAssignmentCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class OperationalEventCreate(BaseModel):
    person_id: int
    project_id: Optional[int] = None
    source: EventSource
    event_type: EventType
    duration_minutes: Optional[float] = None
    event_metadata: Optional[Dict[str, Any]] = None
    started_at: datetime

class OperationalEventRead(OperationalEventCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class MetricSnapshotCreate(BaseModel):
    person_id: int
    week_start: datetime
    meeting_hours: float
    email_count: int
    interruption_count: int
    capacity_hours: float = 40.0
    focus_hours: float
    fragmentation_score: Optional[float] = None

class MetricSnapshotRead(MetricSnapshotCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True