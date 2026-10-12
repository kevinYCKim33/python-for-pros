import os
from collections.abc import Callable, Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# how tests handle environment variables
# needs to run before any module that calls get_settings() is called
# otherwise Pydantic validation error at import time
# and pytest never starts
# a CI environment that supplies its own JWT_SECRET_KEY overrides test default
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "test-secret-key-for-pytest-only-32-bytes",
)

from release_tracker import crud
from release_tracker.config import get_settings
from release_tracker.database import get_engine, get_session
from release_tracker.main import app
from release_tracker.models import User
from release_tracker.security import create_access_token

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
    get_settings.cache_clear()
    get_engine.cache_clear()


@pytest.fixture()
def make_user(session: Session) -> Callable[..., User]:
    def factory(
        *,
        email: str = "testuser@example.com",
        password: str = "testpassword",
        is_active: bool = True,
    ) -> User:
        return crud.create_user(
            session,
            email=email,
            password=password,
            is_active=is_active,
        )

    return factory


@pytest.fixture()
def auth_headers(make_user: Callable[..., User]) -> dict[str, str]:
    user = make_user(email="editor@example.com")
    token = create_access_token(subject=str(user.id))
    return {"Authorization": f"Bearer {token}"}


# so it sees auth_headers above and executes that code
@pytest.fixture()
def auth_client(client: TestClient, auth_headers: dict[str, str]) -> TestClient:
    client.headers.update(auth_headers)
    return client


# now anytime tests need sample_project_id
# they can literally just write sample_project_id
# and get the id
# reduces tons of repetitive code
@pytest.fixture()
def sample_project_id(auth_client: TestClient) -> int:
    response = auth_client.post(
        "/projects/",
        json={
            "name": "Release Platform",
            "description": "Coordinates planning for the production release.",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


@pytest.fixture()
def sample_task_id(auth_client: TestClient, sample_project_id: int) -> int:
    response = auth_client.post(
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
