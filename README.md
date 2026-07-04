# FocusFlow

FocusFlow is an internal workload and focus-fragmentation analytics tool.

## Live Demo

[https://focusflow-api-848897600321.us-east1.run.app](https://focusflow-api-848897600321.us-east1.run.app)

## Why FocusFlow

FocusFlow was born from a real management challenge: how do you advocate
for a team member's workload when you have no visibility into how their
day actually looks?

Context switching, back-to-back meetings, constant interruptions, and
fragmented focus time are invisible in most organisations. Managers make
decisions — about performance, capacity, and expectations — without
concrete data about how work actually happens.

FocusFlow is being built to change that. By tracking operational events,
interruptions, and focus windows, it gives managers and teams the evidence
they need to have honest conversations about workload, capacity, and
organisational design.

## License

Copyright (c) 2026 Chonda Saine. All rights reserved.

This software is proprietary and confidential. It may be viewed for
evaluation and portfolio purposes only. No license is granted to use,
copy, modify, or distribute this software without express written
permission from the copyright owner.

## Privacy Principles

FocusFlow is not an HR tool and is not designed for performance monitoring.

- No personally identifiable information is surfaced in reports or dashboards
- Data is used to identify organisational patterns, not to evaluate individuals
- The goal is to give teams and managers insight to make structural changes
- Individuals own visibility into their own data
- Team summary views aggregate by role, never by individual name

## File Structure

```
FocusFlow/

├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── analytics.py
│   └── seed.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── api.js
│   └── app.js
├── LICENSE
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Database Overview

### people

Stores team members whose workload and focus time will be tracked.

| Column                | Type         | Notes                       |
| --------------------- | ------------ | --------------------------- |
| id                    | SERIAL       | Primary key, auto-increment |
| name                  | VARCHAR(255) | Required                    |
| email                 | VARCHAR(255) | Required, unique            |
| role                  | VARCHAR(100) | Optional                    |
| weekly_capacity_hours | FLOAT        | Optional, defaults to 40.0  |
| created_at            | TIMESTAMP    | Auto-set on insert          |

### projects

Stores client or internal projects that people are assigned to.

| Column      | Type         | Notes                          |
| ----------- | ------------ | ------------------------------ |
| id          | SERIAL       | Primary key, auto-increment    |
| name        | VARCHAR(255) | Required                       |
| client_name | VARCHAR(255) | Optional                       |
| status      | VARCHAR(50)  | Optional, defaults to "active" |
| created_at  | TIMESTAMP    | Auto-set on insert             |

### project_assignments

Links people to projects with an expected hours commitment.

| Column         | Type      | Notes                       |
| -------------- | --------- | --------------------------- |
| id             | SERIAL    | Primary key, auto-increment |
| person_id      | INTEGER   | Foreign key → people.id     |
| project_id     | INTEGER   | Foreign key → projects.id   |
| expected_hours | FLOAT     | Optional                    |
| created_at     | TIMESTAMP | Auto-set on insert          |

### operational_events

Stores raw operational activity — meetings, emails, messages, and
interruptions — for each person. This is the heart of the system.

| Column           | Type      | Notes                                        |
| ---------------- | --------- | -------------------------------------------- |
| id               | SERIAL    | Primary key, auto-increment                  |
| person_id        | INTEGER   | Foreign key → people.id                      |
| project_id       | INTEGER   | Foreign key → projects.id, optional          |
| source           | ENUM      | outlook, teams, slack, gmail, manual         |
| event_type       | ENUM      | meeting, email, direct_message, interruption |
| duration_minutes | FLOAT     | Optional                                     |
| event_metadata   | JSON      | Flexible extra data per event type           |
| started_at       | TIMESTAMP | When the event occurred                      |
| created_at       | TIMESTAMP | Auto-set on insert                           |

### metric_snapshots

Stores pre-calculated weekly summaries per person. Powers dashboards
and trend analysis without recalculating from raw events every time.
`capacity_hours` stores the actual capacity for that specific week.

| Column              | Type      | Notes                                     |
| ------------------- | --------- | ----------------------------------------- |
| id                  | SERIAL    | Primary key, auto-increment               |
| person_id           | INTEGER   | Foreign key → people.id                   |
| week_start          | TIMESTAMP | Start of the week being summarised        |
| meeting_hours       | FLOAT     | Total meeting hours, defaults to 0.0      |
| email_count         | INTEGER   | Total emails, defaults to 0               |
| interruption_count  | INTEGER   | Total interruptions, defaults to 0        |
| capacity_hours      | FLOAT     | Actual capacity for this week, default 40 |
| focus_hours         | FLOAT     | Total focus hours, defaults to 0.0        |
| fragmentation_score | FLOAT     | Calculated score 0-100, optional          |
| created_at          | TIMESTAMP | Auto-set on insert                        |

### ERD

+------------------+ +-------------------------+ +------------------+
| people | | project_assignments | | projects |
+------------------+ +-------------------------+ +------------------+
| id (PK) |←-------| person_id (FK) |------->| id (PK) |
| name | | project_id (FK) | | name |
| email | | expected_hours | | client_name |
| role | | created_at | | status |
| weekly_capacity | +-------------------------+ | created_at |
| created_at | +------------------+
+------------------+
↑
| person_id (FK)
|
+---------------------------+ +---------------------------+
| operational_events | | metric_snapshots |
+---------------------------+ +---------------------------+
| id (PK) | | id (PK) |
| person_id (FK) | | person_id (FK) |
| project_id (FK, optional) | | week_start |
| source | | meeting_hours |
| event_type | | email_count |
| duration_minutes | | interruption_count |
| event_metadata | | focus_hours |
| started_at | | fragmentation_score |
| created_at | | created_at |
+---------------------------+ +---------------------------+

## Fragmentation Score

The fragmentation score is a number from 0 to 100 representing how
fragmented a person's week was. Higher = more fragmented = less
productive focus time.

fragmentation_score = (interruption_count + email_count) / weekly_capacity_hours \* 100

Capped at 100. Calculated automatically when the weekly summary
endpoint is called.

| Event Type     | Counts Toward      |
| -------------- | ------------------ |
| meeting        | meeting_hours      |
| email          | email_count        |
| direct_message | interruption_count |
| interruption   | interruption_count |

## AI Insights

FocusFlow includes an on-demand AI insights engine powered by the
Anthropic API. Clicking **Generate Insights** on the dashboard sends
compressed team fragmentation data to Claude and returns a 3-4 sentence
plain English summary of organisational patterns and recommendations.

- On-demand only — never runs automatically
- Results cached in the browser per week — no duplicate API calls
- Role-level language only — no individual names in insights
- Token usage displayed per call for cost transparency
- Approximately 600 tokens per call — less than $0.001 per insight

## Seed Data

The seed script generates 4 weeks of realistic operational data
simulating a startup under revenue pressure with a project in crisis.

```bash
docker exec -it focusflow-api-1 python app/seed.py
```

| Week   | Narrative                        | Events |
| ------ | -------------------------------- | ------ |
| Week 1 | Baseline — busy but manageable   | 227    |
| Week 2 | Project trouble starts           | 373    |
| Week 3 | Full crisis — peak fragmentation | 584    |
| Week 4 | Stabilising                      | 434    |

People: Chonda Saine, Sondra Williams, Collin Warner, Will Segal,
Matt Barnes, Gabriel Leads across 4 active client projects.

## Roadmap

- [x] Docker setup, PostgreSQL, FastAPI, health endpoints
- [x] people and projects tables, CRUD endpoints
- [x] project_assignments table
- [x] operational_events table
- [x] metric_snapshots table
- [x] Fragmentation score calculation engine
- [x] Seed data script with 4 weeks of realistic data
- [x] Team dashboard API with week-over-week trend
- [x] Per-person 4 week trend endpoint
- [x] Frontend dashboard with branding and dark mode
- [x] Team health summary with role-level aggregation
- [x] Unique constraint on metric_snapshots
- [x] AI insights engine — on-demand, cached, role-level
- [x] Deploy to Google Cloud Run
- [ ] Microsoft 365 integration
- [ ] API usage logging — tokens, cost, cache hit rate
- [ ] Per-org API key management
- [ ] User authentication and multi-tenancy

## Stack

| Layer      | Technology     |
| ---------- | -------------- |
| API        | FastAPI        |
| Database   | PostgreSQL 16  |
| ORM        | SQLAlchemy 2.0 |
| Validation | Pydantic v2    |
| Container  | Docker         |
| Frontend   | HTML/CSS/JS    |
| Charts     | Chart.js 4.4.1 |
| AI         | Anthropic API  |

## Running the App

### Live Deployment

The app is deployed and accessible at:

[https://focusflow-api-848897600321.us-east1.run.app](https://focusflow-api-848897600321.us-east1.run.app)

No setup required — just open the URL in your browser.

### Local Development

```bash
docker compose up --build
```

| Service            | URL                        |
| ------------------ | -------------------------- |
| API                | http://localhost:8000      |
| API Docs (Swagger) | http://localhost:8000/docs |
| pgAdmin            | http://localhost:5050      |

After starting Docker run the seed script to populate the database:

```bash
docker exec -it focusflow-api-1 python app/seed.py
```

## API Endpoints

### Health

| Method | Endpoint   | Description           |
| ------ | ---------- | --------------------- |
| GET    | /health    | API health check      |
| GET    | /health/db | Database health check |

### People

| Method | Endpoint                    | Description                       |
| ------ | --------------------------- | --------------------------------- |
| POST   | /people                     | Create a person                   |
| GET    | /people                     | List all people                   |
| GET    | /people/{id}                | Get one person                    |
| GET    | /people/{id}/weekly_summary | Get weekly summary for one person |
| GET    | /people/{id}/trend          | Get 4 week trend for one person   |

### Projects

| Method | Endpoint       | Description       |
| ------ | -------------- | ----------------- |
| POST   | /projects      | Create a project  |
| GET    | /projects      | List all projects |
| GET    | /projects/{id} | Get one project   |

### Project Assignments

| Method | Endpoint                  | Description          |
| ------ | ------------------------- | -------------------- |
| POST   | /project_assignments      | Create an assignment |
| GET    | /project_assignments      | List all assignments |
| GET    | /project_assignments/{id} | Get one assignment   |

### Operational Events

| Method | Endpoint                 | Description     |
| ------ | ------------------------ | --------------- |
| POST   | /operational_events      | Create an event |
| GET    | /operational_events      | List all events |
| GET    | /operational_events/{id} | Get one event   |

### Metric Snapshots

| Method | Endpoint               | Description        |
| ------ | ---------------------- | ------------------ |
| POST   | /metric_snapshots      | Create a snapshot  |
| GET    | /metric_snapshots      | List all snapshots |
| GET    | /metric_snapshots/{id} | Get one snapshot   |

### Dashboard

| Method | Endpoint          | Description                                   |
| ------ | ----------------- | --------------------------------------------- |
| GET    | /dashboard/weekly | All team members for one week with trend data |

### Insights

| Method | Endpoint         | Description                            |
| ------ | ---------------- | -------------------------------------- |
| GET    | /insights/weekly | AI generated team insight for one week |

## Sprint Log

| Sprint    | What was built                                                  |
| --------- | --------------------------------------------------------------- |
| Sprint 1  | Docker setup, PostgreSQL, FastAPI, health endpoints             |
| Sprint 2  | people and projects tables, CRUD endpoints, pgAdmin             |
| Sprint 3  | project_assignments table, foreign keys, relationships          |
| Sprint 4  | operational_events table, enum fields, JSON metadata field      |
| Sprint 5  | metric_snapshots table, pre-calculated weekly summaries         |
| Sprint 6  | Fragmentation score calculator, weekly summary endpoint         |
| Sprint 7  | Seed data script, 1618 events across 4 weeks, capacity fix      |
| Sprint 8  | Team dashboard API, week-over-week trend, person trend endpoint |
| Sprint 9  | Frontend dashboard, team cards, trend charts, week selector     |
| Sprint 10 | Branding, dark mode, team health summary, unique constraint     |
| Sprint 11 | AI insights engine, frontend refactored into separate files     |
| Sprint 12 | Google Cloud Run deployment, Cloud SQL, live public URL         |
