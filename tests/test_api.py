from fastapi.testclient import TestClient


def test_create_project(auth_client: TestClient) -> None:
    response = auth_client.post(
        "/projects/",
        json={
            "name": "New Project",
            "description": "A test project",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Project"
    assert data["slug"] == "new-project"
    assert "id" in data


def test_get_project(client: TestClient, sample_project_id: int) -> None:
    response = client.get(f"/projects/{sample_project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Release Platform"
    assert data["id"] == sample_project_id


def test_list_projects(client: TestClient, sample_project_id: int) -> None:
    response = client.get("/projects")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["id"] == sample_project_id


def test_update_project(auth_client: TestClient, sample_project_id: int) -> None:
    response = auth_client.patch(
        f"/projects/{sample_project_id}",
        json={"name": "Updated Platform Name"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Platform Name"
    assert data["slug"] == "updated-platform-name"


def test_delete_project(auth_client: TestClient, sample_project_id: int) -> None:
    response = auth_client.delete(f"/projects/{sample_project_id}")
    assert response.status_code == 204

    response = auth_client.get(f"/projects/{sample_project_id}")
    assert response.status_code == 404


def test_create_duplicate_project_fails(auth_client: TestClient, sample_project_id: int) -> None:
    response = auth_client.post(
        "/projects/",
        json={
            "name": "Release Platform",  # Same name as sample_project_id
            "description": "Another description",
        },
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Data conflict occurred (e.g., duplicate entry)."}


def test_create_project_strips_whitespace(auth_client: TestClient) -> None:
    response = auth_client.post(
        "/projects/",
        json={"name": "  Payments API  ", "description": "Handles checkout."},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Payments API"
    assert response.json()["slug"] == "payments-api"


# exercises cascade_delete / ondelete="CASCADE" on Task.project_id
def test_delete_project_removes_its_tasks(auth_client: TestClient, sample_project_id: int) -> None:
    task = auth_client.post(
        f"/projects/{sample_project_id}/tasks",
        json={"title": "Child Task"},
    ).json()

    response = auth_client.delete(f"/projects/{sample_project_id}")
    assert response.status_code == 204

    assert auth_client.get(f"/tasks/{task['id']}").status_code == 404


def test_get_nonexistent_project_returns_404(client: TestClient) -> None:
    response = client.get("/projects/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project 999 not found."


def test_unauthenticated_client_can_list_projects(client: TestClient) -> None:
    # Read endpoints are intentionally public; only write operations require auth.
    response = client.get("/projects/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
