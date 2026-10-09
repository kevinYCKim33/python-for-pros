from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from release_tracker.database import get_engine, get_session
from release_tracker.main import app

# conftest.py: loaded automatically before pytest runs tests


# a fresh in-memory database for each test
@pytest.fixture(name="session")
def session_fixture() -> Generator[Session]:
    # create_engine("sqlite://") => it only lives in memory
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


# builds on the fixture above
@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient]:
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
    get_engine.cache_clear()  # clear cache btw tests


# now anytime tests need sample_project_id
# they can literally just write sample_project_id
# and get the id
# reduces tons of repetitive code
@pytest.fixture()
def sample_project_id(client: TestClient) -> int:
    response = client.post(
        "/projects/",
        json={
            "name": "Release Platform",
            "description": "Coordinates planning for the production release.",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


@pytest.fixture()
def sample_task_id(client: TestClient, sample_project_id: int) -> int:
    response = client.post(
        f"/projects/{sample_project_id}/tasks",
        json={
            "title": "Wire up the dashboard",
            "details": "Connect the API to the static frontend.",
            "status": "planned",
            "priority": "medium",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]
