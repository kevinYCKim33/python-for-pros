from fastapi.testclient import TestClient


# asks for @pytest.fixture(name="client")
# which asks for @pytest.fixture(name="session")
def test_get_task_not_found(client: TestClient):
    response = client.get("/tasks/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


# asks for fixture client which asks for fixture session
# asks for sample_project_id
def test_list_tasks_filter_by_status(client: TestClient, sample_project_id: int):
    client.post(
        f"/projects/{sample_project_id}/tasks",
        json={"title": "Planned task", "status": "planned"},
    )
    client.post(
        f"/projects/{sample_project_id}/tasks",
        json={"title": "Done task", "status": "done"},
    )

    response = client.get("/tasks", params={"status": "done"})
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Done task"]


def test_create_task(client: TestClient, sample_project_id: int):
    response = client.post(
        f"/projects/{sample_project_id}/tasks",
        json={
            "title": "Add settings page",
            "priority": "high",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Add settings page"
    assert data["status"] == "planned"
    assert data["priority"] == "high"
    assert data["project_id"] == sample_project_id
    assert data["project_name"] == "Release Platform"
    assert data["project_slug"] == "release-platform"


def test_get_task(client: TestClient, sample_task_id: int):
    response = client.get(f"/tasks/{sample_task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == sample_task_id


def test_list_tasks_filter_by_project_slug(client: TestClient, sample_project_id: int):
    other = client.post(
        "/projects/",
        json={"name": "Other Project", "description": "unrelated"},
    ).json()
    client.post(
        f"/projects/{sample_project_id}/tasks",
        json={"title": "First task"},
    )
    client.post(
        f"/projects/{other['id']}/tasks",
        json={"title": "Second task"},
    )

    response = client.get("/tasks", params={"project_slug": other["slug"]})
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Second task"]


def test_update_task(client: TestClient, sample_task_id: int):
    response = client.patch(
        f"/tasks/{sample_task_id}",
        json={"status": "in_progress", "priority": "urgent"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["priority"] == "urgent"


def test_delete_task(client: TestClient, sample_task_id: int):
    response = client.delete(f"/tasks/{sample_task_id}")
    assert response.status_code == 204

    follow_up = client.get(f"/tasks/{sample_task_id}")
    assert follow_up.status_code == 404


def test_create_task_for_missing_project_returns_404(client: TestClient):
    response = client.post(
        "/projects/9999/tasks",
        json={"title": "Orphan"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}
