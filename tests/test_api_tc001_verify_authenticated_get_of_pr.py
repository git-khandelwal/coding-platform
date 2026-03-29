import os
import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
TEST_USERNAME = os.getenv("TEST_USERNAME", "testuser")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "testpass")


@pytest.fixture(scope="session")
def auth_token():
    """Obtain a JWT by logging in with known credentials."""
    login_url = f"{BASE_URL}/login"
    payload = {"username": TEST_USERNAME, "password": TEST_PASSWORD}
    response = requests.post(login_url, json=payload)
    assert response.status_code == 200, f"Login request failed: {response.status_code} {response.text}"
    data = response.json()
    token = data.get("access_token") or data.get("token")
    assert token, "JWT token not found in login response"
    return token


def test_tc001_authenticated_get_protected_endpoint(auth_token):
    """TC001 – Verify authenticated GET of protected endpoint returns correct username."""
    protected_url = f"{BASE_URL}/protected"
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(protected_url, headers=headers)

    # Expected Result: request succeeds with 200 OK
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    # Expected Result: response body contains `logged_in_as` with the correct username
    json_body = response.json()
    assert "logged_in_as" in json_body, "Response JSON missing 'logged_in_as' field"
    assert (
        json_body["logged_in_as"] == TEST_USERNAME
    ), f"Expected logged_in_as to be '{TEST_USERNAME}', got '{json_body['logged_in_as']}'"