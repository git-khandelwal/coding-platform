import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="function")
def unique_user_credentials():
    # Generate unique username for isolation
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "TestPassword123!"
    return {"username": username, "password": password}

@pytest.fixture(scope="function")
def register_user(unique_user_credentials):
    url = f"{BASE_URL}/register"
    response = requests.post(url, json=unique_user_credentials)
    # Registration should succeed for unique user, but this is not the focus of this test
    # If registration fails, the login test would be invalid
    assert response.status_code == 201, f"User registration failed: {response.text}"
    return unique_user_credentials

def test_login_with_valid_credentials(register_user):
    """
    TC004: Login with Valid Credentials
    Steps:
    1. Register a user (handled by fixture).
    2. Send POST request to /login with valid credentials.
    Expected:
    - Response status is 200.
    - Response body contains "access_token".
    """
    login_url = f"{BASE_URL}/login"
    credentials = register_user
    response = requests.post(login_url, json=credentials)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    json_data = response.json()
    assert "access_token" in json_data, f"Response JSON does not contain 'access_token': {json_data}"
    assert isinstance(json_data["access_token"], str) and len(json_data["access_token"]) > 0, "access_token is not a valid string"