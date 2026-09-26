from fastapi.testclient import TestClient

from release_tracker.main import app

client = TestClient(app)


def test_list_projects():
    response = client.get("/projects")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_list_projects_by_slug():
    response = client.get("/projects", params={"slug": "api-v2"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["slug"] == "api-v2"


def test_get_project():
    response = client.get("/projects/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Frontend Redesign"


def test_get_project_not_found():
    response = client.get("/projects/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"
