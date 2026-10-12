from fastapi.testclient import TestClient


def test_root_describes_the_service(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["app"] == "Release Tracker API"
    assert response.json()["docs"] == "/docs"


def test_healthcheck_returns_healthy(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_dashboard_page_is_served(client: TestClient) -> None:
    response = client.get("/app")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "release-tracker-dashboard" in response.text
