from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum

class Person(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    role = Column(String(100), nullable=True)
    weekly_capacity_hours = Column(Float, nullable=True, default=40.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    client_name = Column(String(255), nullable=True)
    status = Column(String(50), nullable=True, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ProjectAssignment(Base):
    __tablename__ = "project_assignments"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("people.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    expected_hours = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class EventType(enum.Enum):
    meeting = "meeting"
    email = "email"
    direct_message = "direct_message"
    interruption = "interruption"

class EventSource(enum.Enum):
    outlook = "outlook"
    teams = "teams"
    slack = "slack"
    gmail = "gmail"
    manual = "manual"

class OperationalEvent(Base):
    __tablename__ = "operational_events"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("people.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    source = Column(Enum(EventSource), nullable=False)
    event_type = Column(Enum(EventType), nullable=False)
    duration_minutes = Column(Float, nullable=True)
    event_metadata = Column(JSON, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MetricSnapshots(Base):
    __tablename__ = "metric_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("people.id"), nullable=False)
    week_start = Column(DateTime(timezone=True), nullable=False)
    meeting_hours = Column(Float, nullable=False, default=0.0)
    email_count = Column(Integer, nullable=False, default=0)
    interruption_count = Column(Integer, nullable=False, default=0)
    capacity_hours = Column(Float, nullable=False, default=40.0)
    focus_hours = Column(Float, nullable=False, default=0.0)
    fragmentation_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    