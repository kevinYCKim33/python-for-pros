from fastapi.testclient import TestClient


def test_create_project(client: TestClient):
    response = client.post(
        "/projects",
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


def test_get_project(client: TestClient, sample_project_id: int):
    response = client.get(f"/projects/{sample_project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Release Platform"
    assert data["id"] == sample_project_id


def test_list_projects(client: TestClient, sample_project_id: int):
    response = client.get("/projects")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["id"] == sample_project_id


def test_update_project(client: TestClient, sample_project_id: int):
    response = client.patch(
        f"/projects/{sample_project_id}",
        json={"name": "Updated Platform Name"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Platform Name"
    assert data["slug"] == "updated-platform-name"


def test_delete_project(client: TestClient, sample_project_id: int):
    response = client.delete(f"/projects/{sample_project_id}")
    assert response.status_code == 204

    response = client.get(f"/projects/{sample_project_id}")
    assert response.status_code == 404
