from fastapi.testclient import TestClient

# Import the FastAPI 'app' instance from our main code
from release_tracker.main import app

# Create a TestClient using our app
client = TestClient(app)


def test_list_projects():
    # Simulate a GET request to the /projects URL
    response = client.get("/projects")

    # Assert that the HTTP status code is 200 (Success)
    assert response.status_code == 200

    # Assert that the JSON response body is a list with 1 item.
    assert len(response.json()) == 3
