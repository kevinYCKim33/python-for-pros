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
