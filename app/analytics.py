from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
import pytz
import os
import anthropic
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

def get_team_dashboard(db: Session, week_start: datetime):
    week_start_est, week_end_est = get_week_boundaries(week_start)
    last_week_start = week_start_est - timedelta(days=7)

    snapshots = db.query(MetricSnapshots).filter(
        and_(
            MetricSnapshots.week_start >= week_start_est,
            MetricSnapshots.week_start < week_end_est
        )
    ).all()

    if not snapshots:
        return {
            "week_start": week_start_est.isoformat(),
            "generated_at": datetime.now(EST).isoformat(),
            "team": [],
            "message": "No data found for this week."
        }

    team = []
    for snapshot in snapshots:
        person = db.query(Person).filter(Person.id == snapshot.person_id).first()

        last_week_snapshot = db.query(MetricSnapshots).filter(
            and_(
                MetricSnapshots.person_id == snapshot.person_id,
                MetricSnapshots.week_start >= last_week_start,
                MetricSnapshots.week_start < week_start_est
            )
        ).first()

        if last_week_snapshot and last_week_snapshot.fragmentation_score is not None and snapshot.fragmentation_score is not None:
            trend = round(snapshot.fragmentation_score - last_week_snapshot.fragmentation_score, 2)
            trend_direction = "worse" if trend > 0 else "better" if trend < 0 else "unchanged"
        else:
            trend = None
            trend_direction = "no_previous_data"

        team.append({
            "person_id": snapshot.person_id,
            "name": person.name if person else "Unknown",
            "role": person.role if person else "Unknown",
            "fragmentation_score": snapshot.fragmentation_score,
            "meeting_hours": snapshot.meeting_hours,
            "email_count": snapshot.email_count,
            "interruption_count": snapshot.interruption_count,
            "focus_hours": snapshot.focus_hours,
            "capacity_hours": snapshot.capacity_hours,
            "fragmentation_trend": trend,
            "trend_direction": trend_direction
        })

    team.sort(key=lambda x: x["fragmentation_score"] or 0, reverse=True)

    return {
        "week_start": week_start_est.isoformat(),
        "generated_at": datetime.now(EST).isoformat(),
        "team": team,
        "message": "Team dashboard generated successfully."
    }

def get_person_trend(db: Session, person_id: int):
    person = db.query(Person).filter(Person.id == person_id).first()
    if person is None:
        return None

    snapshots = db.query(MetricSnapshots).filter(
        MetricSnapshots.person_id == person_id
    ).order_by(MetricSnapshots.week_start).all()

    if not snapshots:
        return {
            "person_id": person_id,
            "name": person.name,
            "role": person.role,
            "weeks": [],
            "message": "No data found for this person."
        }

    weeks = []
    for snapshot in snapshots:
        weeks.append({
            "week_start": snapshot.week_start.isoformat(),
            "fragmentation_score": snapshot.fragmentation_score,
            "meeting_hours": snapshot.meeting_hours,
            "email_count": snapshot.email_count,
            "interruption_count": snapshot.interruption_count,
            "focus_hours": snapshot.focus_hours,
            "capacity_hours": snapshot.capacity_hours
        })

    return {
        "person_id": person_id,
        "name": person.name,
        "role": person.role,
        "weeks": weeks,
        "message": "Trend data retrieved successfully."
    }

def generate_team_insights(db: Session, week_start: datetime) -> dict:
    dashboard = get_team_dashboard(db=db, week_start=week_start)

    if not dashboard["team"]:
        return {
            "insight": "No data available for this week.",
            "cached": False,
            "week_start": dashboard["week_start"]
        }

    team = dashboard["team"]
    avg_score = round(sum(p["fragmentation_score"] or 0 for p in team) / len(team), 1)
    total_meetings = round(sum(p["meeting_hours"] for p in team), 1)
    total_interruptions = sum(p["interruption_count"] for p in team)
    total_emails = sum(p["email_count"] for p in team)

    most_deteriorated = next(
        (p for p in sorted(team, key=lambda x: x.get("fragmentation_trend") or 0, reverse=True)
         if p.get("trend_direction") == "worse"), None
    )

    most_improved = next(
        (p for p in sorted(team, key=lambda x: x.get("fragmentation_trend") or 0)
         if p.get("trend_direction") == "better"), None
    )

    compressed = f"""
Week: {dashboard["week_start"]}
Team size: {len(team)}
Average fragmentation score: {avg_score}/100
Team status: {("Critical" if avg_score > 70 else "At Risk" if avg_score > 40 else "Healthy")}
Total meeting hours across team: {total_meetings}h
Total interruptions across team: {total_interruptions}
Total emails across team: {total_emails}

Role breakdown:
{chr(10).join(f"- {p['role']}: score {p['fragmentation_score']}, {p['meeting_hours']}h meetings, {p['email_count']} emails, {p['interruption_count']} interruptions, trend: {p['trend_direction']}" for p in team)}

Most deteriorated role: {most_deteriorated['role'] if most_deteriorated else 'none'} ({f"+{most_deteriorated['fragmentation_trend']} pts" if most_deteriorated else 'n/a'})
Most improved role: {most_improved['role'] if most_improved else 'none'} ({f"{most_improved['fragmentation_trend']} pts" if most_improved else 'n/a'})
"""

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": f"""You are an organisational analytics assistant for a startup.
Analyse this team fragmentation data and provide exactly 3-4 sentences of insight.
Focus on organisational patterns, workload distribution, and actionable recommendations.
Use role names not individual names. Be direct and specific about what the numbers mean.
Never use bullet points — write in plain prose only.

Data:
{compressed}"""
            }
        ]
    )

    insight = message.content[0].text

    return {
        "insight": insight,
        "cached": False,
        "week_start": dashboard["week_start"],
        "tokens_used": message.usage.input_tokens + message.usage.output_tokens
    }