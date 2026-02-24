import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="function")
def test_user():
    """
    Fixture to generate a unique username and password for testing.
    Registers the user before yielding credentials.
    """
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "TestPassword123!"
    register_resp = requests.post(
        f"{BASE_URL}/register",
        json={"username": username, "password": password}
    )
    # Registration should succeed (201) or, if user exists, fail (but this should not happen with uuid)
    assert register_resp.status_code == 201, f"Registration failed: {register_resp.text}"
    yield {"username": username, "password": password}
    # No teardown needed; test DB should be cleaned externally


@pytest.fixture(scope="function")
def access_token(test_user):
    """
    Fixture to log in the test user and return a valid JWT access token.
    """
    login_resp = requests.post(
        f"{BASE_URL}/login",
        json={"username": test_user["username"], "password": test_user["password"]}
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    data = login_resp.json()
    assert "access_token" in data, "No access_token in login response"
    return data["access_token"]


def test_access_protected_route_with_valid_token(test_user, access_token):
    """
    TC006: Access Protected Route with Valid Token
    1. Register and login to get token.
    2. Send GET request to protected route with Authorization header.
    Expected:
    - Response status is 200 OK.
    - Response contains "logged_in_as" with correct username.
    """
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    resp = requests.get(f"{BASE_URL}/protected", headers=headers)
    assert resp.status_code == 200, f"Expected 200 OK, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "logged_in_as" in data, f'"logged_in_as" not in response: {data}'
    assert data["logged_in_as"] == test_user["username"], (
        f'Expected logged_in_as="{test_user["username"]}", got "{data["logged_in_as"]}"'
    )