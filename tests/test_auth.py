from collections.abc import Callable
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from release_tracker.models import User
from release_tracker.security import create_access_token


def test_login_returns_token(client: TestClient, make_user: Callable[..., User]) -> None:
    make_user(email="login@example.com", password="correct-password")

    response = client.post(
        "/auth/token",
        data={
            "username": "login@example.com",
            "password": "correct-password",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert len(body["access_token"]) > 0


def test_login_wrong_password_returns_401(
    client: TestClient, make_user: Callable[..., User]
) -> None:
    make_user(email="login@example.com", password="correct-password")

    response = client.post(
        "/auth/token",
        data={
            "username": "login@example.com",
            "password": "WRONG",
        },
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email or password"}


def test_login_unknown_user_returns_401(client: TestClient) -> None:
    response = client.post(
        "/auth/token",
        data={
            "username": "nobody@example.com",
            "password": "anything",
        },
    )
    assert response.status_code == 401


def test_inactive_user_cannot_log_in(client: TestClient, make_user: Callable[..., User]) -> None:
    make_user(email="frozen@example.com", password="pw", is_active=False)

    response = client.post(
        "/auth/token",
        data={
            "username": "frozen@example.com",
            "password": "pw",
        },
    )
    assert response.status_code == 401


def test_me_endpoint_returns_current_user(auth_client: TestClient) -> None:
    response = auth_client.get("/auth/me")
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "editor@example.com"
    assert body["is_active"] is True
    assert "hashed_password" not in body


def test_me_endpoint_rejects_missing_token(client: TestClient) -> None:
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_endpoint_rejects_garbage_token(client: TestClient) -> None:
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer not-a-real-jwt"},
    )
    assert response.status_code == 401


def test_register_creates_user(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={"email": "new@example.com", "password": "s3cret-pass"},
    )
    assert response.status_code == 201
    body = response.json()  # brings the json back to python land
    # true => True; null => None
    assert body["email"] == "new@example.com"
    assert body["is_active"] is True
    assert "hashed_password" not in body


def test_register_then_login(client: TestClient) -> None:
    client.post(
        "/auth/register",
        json={"email": "fresh@example.com", "password": "my-password"},
    )

    response = client.post(
        "/auth/token",
        # log in with the same user
        data={"username": "fresh@example.com", "password": "my-password"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_failure_sends_www_authenticate_header(client: TestClient) -> None:
    response = client.post(
        "/auth/token",
        data={"username": "nobody@example.com", "password": "anything"},
    )
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_expired_token_rejected(client: TestClient, make_user: Callable[..., User]) -> None:
    user = make_user(email="expired@example.com")
    # Create a token that expired 1 hour ago
    token = create_access_token(subject=str(user.id), expires_delta=timedelta(minutes=-60))

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


# parametrize: same test body runs once per (method, endpoint) pair
@pytest.mark.parametrize(
    ("method", "endpoint"),
    [
        ("POST", "/projects/"),
        ("PATCH", "/projects/1"),
        ("DELETE", "/projects/1"),
        ("POST", "/projects/1/tasks"),
        ("PATCH", "/tasks/1"),
        ("DELETE", "/tasks/1"),
    ],
)
def test_write_endpoints_require_authentication(
    client: TestClient, method: str, endpoint: str
) -> None:
    response = client.request(
        method,
        endpoint,
        json={"name": "Unauthorized Project", "title": "Unauthorized Task"},
    )
    assert response.status_code == 401
