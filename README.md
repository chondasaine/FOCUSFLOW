# FocusFlow

FocusFlow is an internal workload and focus-fragmentation analytics tool.

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

## Privacy Principles

FocusFlow is not an HR tool and is not designed for performance monitoring.

- No personally identifiable information is surfaced in reports or dashboards
- Data is used to identify organisational patterns, not to evaluate individuals
- The goal is to give teams and managers insight to make structural changes
- Individuals own visibility into their own data

## File Structure

```
app/
├── main.py
├── database.py
├── models.py
├── schemas.py
└── crud.py
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

| Column              | Type      | Notes                                |
| ------------------- | --------- | ------------------------------------ |
| id                  | SERIAL    | Primary key, auto-increment          |
| person_id           | INTEGER   | Foreign key → people.id              |
| week_start          | TIMESTAMP | Start of the week being summarised   |
| meeting_hours       | FLOAT     | Total meeting hours, defaults to 0.0 |
| email_count         | INTEGER   | Total emails, defaults to 0          |
| interruption_count  | INTEGER   | Total interruptions, defaults to 0   |
| focus_hours         | FLOAT     | Total focus hours, defaults to 0.0   |
| fragmentation_score | FLOAT     | Calculated score 0-100, optional     |
| created_at          | TIMESTAMP | Auto-set on insert                   |

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

## Roadmap

- [x] Docker setup, PostgreSQL, FastAPI, health endpoints
- [x] people and projects tables, CRUD endpoints
- [x] project_assignments table
- [x] operational_events table
- [x] metric_snapshots table
- [ ] Fragmentation score calculation engine
- [ ] Microsoft 365 integration
- [ ] Dashboard API

## Stack

| Layer      | Technology     |
| ---------- | -------------- |
| API        | FastAPI        |
| Database   | PostgreSQL 16  |
| ORM        | SQLAlchemy 2.0 |
| Validation | Pydantic v2    |
| Container  | Docker         |

## Running the App

```bash
docker compose up --build
```

| Service            | URL                        |
| ------------------ | -------------------------- |
| API                | http://localhost:8000      |
| API Docs (Swagger) | http://localhost:8000/docs |
| pgAdmin            | http://localhost:5050      |

## API Endpoints

### Health

| Method | Endpoint   | Description           |
| ------ | ---------- | --------------------- |
| GET    | /health    | API health check      |
| GET    | /health/db | Database health check |

### People

| Method | Endpoint     | Description     |
| ------ | ------------ | --------------- |
| POST   | /people      | Create a person |
| GET    | /people      | List all people |
| GET    | /people/{id} | Get one person  |

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

## Sprint Log

| Sprint   | What was built                                             |
| -------- | ---------------------------------------------------------- |
| Sprint 1 | Docker setup, PostgreSQL, FastAPI, health endpoints        |
| Sprint 2 | people and projects tables, CRUD endpoints, pgAdmin        |
| Sprint 3 | project_assignments table, foreign keys, relationships     |
| Sprint 4 | operational_events table, enum fields, JSON metadata field |
| Sprint 5 | metric_snapshots table, pre-calculated weekly summaries    |
