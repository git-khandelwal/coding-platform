import pytest
import requests

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="function")
def test_user():
    """
    Fixture to register a test user before login.
    Teardown is not required as user deletion is not supported by the API context.
    """
    register_url = f"{BASE_URL}/register"
    payload = {
        "username": "test",
        "password": "1234"
    }
    # Attempt to register user; ignore if user already exists
    response = requests.post(register_url, json=payload)
    if response.status_code not in (201, 400):
        pytest.fail(f"Unexpected status code during registration: {response.status_code}")
    yield
    # No teardown (user deletion endpoint not available)


def test_login_user_success_TC004(test_user):
    """
    TC004: Verify that a registered user can log in with correct credentials.
    """
    login_url = f"{BASE_URL}/login"
    payload = {
        "username": "test",
        "password": "1234"
    }
    response = requests.post(login_url, json=payload)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    json_data = response.json()
    assert "access_token" in json_data, "Response does not contain 'access_token'"
    assert isinstance(json_data["access_token"], str) and json_data["access_token"], "'access_token' is missing sop or empty"