import pytest
import requests

BASE_URL = "http://localhost:5000"


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the API under test."""
    return BASE_URL.rstrip("/")


@pytest.fixture(scope="session")
def test_user():
    """Credentials for an existing test user."""
    return {"username": "testuser", "password": "testpassword"}


@pytest.fixture
def jwt_token(base_url, test_user):
    """
    Obtain a valid JWT by logging in.
    Assumes a POST /login endpoint that returns JSON {"access_token": "<token>"}.
    """
    login_url = f"{base_url}/login"
    response = requests.post(login_url, json=test_user)
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "access_token" in data, "Login response missing access_token"
    return data["access_token"]


def test_protected_endpoint_with_valid_jwt(base_url, test_user, jwt_token):
    """
    TC001: Verify access to protected endpoint with valid JWT.
    Steps:
    1. Obtain a valid JWT (handled by jwt_token fixture).
    2. GET /protected with Authorization header.
    3. Validate response.
    """
    protected_url = f"{base_url}/protected"
    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(protected_url, headers=headers)

    # Expected Result assertions
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    json_body = response.json()
    assert "logged_in_as" in json_body, "Response missing 'logged_in_as' field"
    assert json_body["logged_in_as"] == test_user["username"], (
        f"Expected logged_in_as to be '{test_user['username']}', "
        f"got '{json_body['logged_in_as']}'"
    )
    # Ensure no error messages are present
    assert not json_body.get("error"), f"Unexpected error in response: {json_body.get('error')}"