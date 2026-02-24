import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="function")
def valid_user_credentials():
    """
    Fixture to generate unique valid user credentials for registration and login.
    """
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "TestPassword123!"
    return {"username": unique_username, "password": password}

@pytest.fixture(scope="function")
def register_user(valid_user_credentials):
    """
    Fixture to register a user using the provided credentials.
    """
    register_url = f"{BASE_URL}/register"
    response = requests.post(register_url, json=valid_user_credentials)
    # Registration should succeed with 201 Created
    assert response.status_code == 201
    assert response.json().get("message") == "User registered successfully"
    return valid_user_credentials

def test_login_with_valid_credentials(register_user):
    """
    TC004: Login with Valid Credentials
    Steps:
      1. Register a user.
      2. Send POST request to login with correct credentials.
    Expected Result:
      1. Response status is 200 OK.
      2. Response contains "access_token".
    """
    login_url = f"{BASE_URL}/login"
    credentials = register_user

    response = requests.post(login_url, json=credentials)

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    json_data = response.json()
    assert "access_token" in json_data, "Response does not contain 'access_token'"
    assert isinstance(json_data["access_token"], str) and json_data["access_token"], "'access_token' is missing or empty"