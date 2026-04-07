import uuid
import requests
import pytest

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def registered_user():
    """
    Register a new user before running the test.
    Returns a tuple of (username, password).
    """
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "TestPass123!"

    register_payload = {"username": username, "password": password}
    response = requests.post(f"{BASE_URL}/register", json=register_payload)

    assert response.status_code == 201, f"Registration failed: {response.text}"
    assert (
        response.json().get("message") == "User registered successfully"
    ), f"Unexpected registration message: {response.text}"

    yield username, password

    # Teardown: optionally delete the user if the API supports it
    # For now, we assume the user remains in the test database


def test_login_success(registered_user):
    """
    TC004: Verify that a registered user can log in and receive a JWT token.
    """
    username, password = registered_user
    login_payload = {"username": username, "password": password}
    response = requests.post(f"{BASE_URL}/login", json=login_payload)

    assert response.status_code == 200, f"Login failed: {response.text}"
    json_resp = response.json()
    assert "access_token" in json_resp, "Response does not contain access_token"
    assert isinstance(json_resp["access_token"], str) and len(json_resp["access_token"]) > 0, (
        "access_token is not a non-empty string"
    )