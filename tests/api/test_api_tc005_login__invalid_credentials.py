import uuid
import pytest
import requests

BASE_URL = "http://localhost:5000"


@pytest.fixture(scope="session")
def registered_user():
    """
    Register a unique user before running the test session.
    Returns a dictionary with the username and password.
    """
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "SecurePass123!"
    payload = {"username": username, "password": password}
    response = requests.post(f"{BASE_URL}/register", json=payload)
    assert response.status_code == 201, f"Registration failed: {response.text}"
    return {"username": username, "password": password}


def test_login_invalid_credentials(registered_user):
    """
    TC005: Verify that login fails with incorrect username or password.
    """
    # Use the registered username but an incorrect password
    payload = {
        "username": registered_user["username"],
        "password": "WrongPassword!"
    }
    response = requests.post(f"{BASE_URL}/login", json=payload)

    # Assert status code 401
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    # Assert error message in response body
    json_resp = response.json()
    assert "error" in json_resp, "Response JSON does not contain 'error' key"
    assert (
        json_resp["error"] == "Invalid username or password"
    ), f"Unexpected error message: {json_resp['error']}"