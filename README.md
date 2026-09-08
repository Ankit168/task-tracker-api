# Task Tracker API

A FastAPI task-management API backed by SQLite and SQLAlchemy.

## Features

- Create, list, update, and delete tasks
- Filter tasks by completion status
- Input validation with Pydantic
- SQLite database persistence
- Automated tests with pytest
- Interactive API documentation

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run locally

```bash
uvicorn main:app --reload
```

Open the interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

```text
GET    /health
POST   /tasks
GET    /tasks
GET    /tasks/{task_id}
PATCH  /tasks/{task_id}
DELETE /tasks/{task_id}
```

Filter incomplete tasks:

```text
GET /tasks?completed=false
```

## Tests

```bash
pytest
```