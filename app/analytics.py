from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
import pytz
from app.models import OperationalEvent, MetricSnapshots, Person, EventType


EST = pytz.timezone("US/Eastern")

def get_week_boundaries(week_start: datetime):
    week_start_est = EST.localize(week_start.replace(tzinfo=None))
    week_end_est = week_start_est + timedelta(days=7)
    return week_start_est, week_end_est

def calculate_weekly_summary(db: Session, person_id: int, week_start: datetime, capacity_hours: float = None):
    person = db.query(Person).filter(Person.id == person_id).first()
    if person is None:
        return None
    
    week_start_est, week_end_est = get_week_boundaries(week_start)

    events = db.query(OperationalEvent).filter(
        and_(
            OperationalEvent.person_id == person_id,
            OperationalEvent.started_at >= week_start_est,
            OperationalEvent.started_at < week_end_est
        )
    ).all()

    if not events:
        return {
            "person_id": person_id,
            "week_start": week_start_est.isoformat(),
            "meeting_hours": 0.0,
            "email_count": 0,
            "interruption_count": 0,
            "focus_hours": 0.0,
            "fragmentation_score": None,
            "no_events": True,
            "message": "No events found for this week yet."
        }
    
    meeting_minutes = sum(
        e.duration_minutes or 0
        for e in events
        if e.event_type == EventType.meeting
    )
    meeting_hours = round(meeting_minutes / 60, 2)

    email_count = sum(
        1 for e in events
        if e.event_type == EventType.email
    )

    interruption_count = sum(
        1 for e in events
        if e.event_type in [EventType.direct_message, EventType.interruption]
    )

    weekly_capacity = capacity_hours or person.weekly_capacity_hours or 40.0
    focus_hours = round(max(weekly_capacity - meeting_hours, 0), 2)

    raw_score = (interruption_count + email_count) / weekly_capacity * 100
    fragmentation_score = round(min(raw_score, 100), 2)

    snapshot = MetricSnapshots(
        person_id=person_id,
        week_start=week_start_est,
        meeting_hours=meeting_hours,
        email_count=email_count,
        interruption_count=interruption_count,
        focus_hours=focus_hours,
        fragmentation_score=fragmentation_score,
        capacity_hours=weekly_capacity
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    return {
        "person_id": person_id,
        "week_start": week_start_est.isoformat(),
        "meeting_hours": meeting_hours,
        "email_count": email_count,
        "interruption_count": interruption_count,
        "focus_hours": focus_hours,
        "fragmentation_score": fragmentation_score,
        "no_events": False,
        "message": "Weekly summary calculated successfully."
    }