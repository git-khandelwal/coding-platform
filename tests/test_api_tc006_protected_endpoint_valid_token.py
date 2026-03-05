import os
import pytest
import requests

# Base URL of the running Flask application. Adjust if the app runs on a different host/port.
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

# Test user credentials. These should be unique for each test run to avoid conflicts.
TEST_USERNAME = "test_user_tc006"
TEST_PASSWORD = "SecurePass123!"

@pytest.fixture(scope="module")
def register_user():
    """
    Register a new user for testing. If the user already exists, the test will
    proceed assuming the user is available.
    """
    register_url = f"{BASE_URL}/register"
    payload = {"username": TEST_USERNAME, "password": TEST_PASSWORD}
    response = requests.post(register_url, json=payload)

    # If registration fails due to existing user, ignore the error.
    if response.status_code not in (201, 400):
        pytest.fail(f"Unexpected status code during registration: {response.status_code}")

    # Return the credentials for downstream use
    return {"username": TEST_USERNAME, "password": TEST_PASSWORD}


@pytest.fixture(scope="module")
def jwt_token(register_user):
    """
    Obtain a JWT token by logging in with the registered user.
    """
    login_url = f"{BASE_URL}/login"
    payload = {"username": register_user["username"], "password": register_user["password"]}
    response = requests.post(login_url, json=payload)

    assert response.status_code == 200, f"Login failed with status {response.status_code}"
    data = response.json()
    assert "access_token" in data, "Response does not contain access_token"

    return data["access_token"]


def test_protected_endpoint_valid_token(jwt_token, register_user):
    """
    TC006: Verify that the protected endpoint is accessible with a valid JWT.
    """
    protected_url = f"{BASE_URL}/protected"
    headers = {"Authorization": f"Bearer {jwt_token}"}

    response = requests.get(protected_url, headers=headers)

    # Expected Result: Status 200 OK
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    # Expected Result: Response body contains `logged_in_as` with the correct username
    data = response.json()
    assert "logged_in_as" in data, "Response JSON missing 'logged_in_as' key"
    assert data["logged_in_as"] == register_user["username"], (
        f"Expected logged_in_as to be '{register_user['username']}', "
        f"got '{data['logged_in_as']}'"
    )