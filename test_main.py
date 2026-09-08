import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
)


def override_get_db():
    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


def test_create_task():
    response = client.post(
        "/tasks",
        json={
            "title": "Write tests",
            "description": "Test task creation",
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["title"] == "Write tests"
    assert response.json()["completed"] is False


def test_filter_incomplete_tasks():
    client.post("/tasks", json={"title": "Incomplete task"})

    completed_task = client.post(
        "/tasks",
        json={"title": "Completed task"},
    )
    task_id = completed_task.json()["id"]

    client.patch(
        f"/tasks/{task_id}",
        json={"completed": True},
    )

    response = client.get(
        "/tasks",
        params={"completed": False},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Incomplete task"

def test_update_task():
    created = client.post(
        "/tasks",
        json={"title": "Original title"},
    )
    task_id = created.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={
            "title": "Updated title",
            "completed": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated title"
    assert response.json()["completed"] is True


def test_delete_task():
    created = client.post(
        "/tasks",
        json={"title": "Task to delete"},
    )
    task_id = created.json()["id"]

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 204

    missing_task = client.get(f"/tasks/{task_id}")

    assert missing_task.status_code == 404