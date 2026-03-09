import pytest
from app import app as flask_app  # Assumes the Flask application instance is exposed as `app` in the package `app`

@pytest.fixture
def client():
    """
    Provides a Flask test client for the application.
    """
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client

def test_register_missing_fields(client):
    """
    Test Case TC002: User Registration – Missing Fields
    Attempts to register a user with either the username or password omitted
    and verifies that the API responds with a 400 status code and the
    appropriate error message.
    """
    # Scenario 1: Missing username
    payload_missing_username = {"password": "SecurePass123"}
    response = client.post("/register", json=payload_missing_username)
    assert response.status_code == 400, "Expected status code 400 for missing username"
    json_data = response.get_json()
    assert json_data is not None, "Response should contain JSON data"
    assert json_data.get("error") == "Username and password are required", (
        "Expected error message for missing username"
    )

    # Scenario 2: Missing password
    payload_missing_password = {"username": "testuser"}
    response = client.post("/register", json=payload_missing_password)
    assert response.status_code == 400, "Expected status code 400 for missing password"
    json_data = response.get_json()
    assert json_data is not None, "Response should contain JSON data"
    assert json_data.get("error") == "Username and password are required", (
        "Expected error message for missing password"
    )