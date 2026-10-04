from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from release_tracker.database import get_engine, get_session
from release_tracker.main import app


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient]:
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
    get_engine.cache_clear()


@pytest.fixture()
def sample_project_id(client: TestClient) -> int:
    response = client.post(
        "/projects",
        json={
            "name": "Release Platform",
            "description": "Coordinates planning for the production release.",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]
