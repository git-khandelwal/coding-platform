import pytest
import requests
import uuid

# Note: Base URL is assumed to be localhost:5000 based on standard Flask development patterns.
# If the environment requires a different host, this should be configured via environment variables.
BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def registered_user():
    """
    Setup: Create a unique user to ensure the login test has valid credentials.
    """
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "securePassword123"
    
    payload = {"username": username, "password": password}
    response = requests.post(f"{BASE_URL}/register", json=payload)
    
    if response.status_code != 201:
        pytest.fail(f"Setup failed: Could not register user. Response: {response.text}")
    
    return {"username": username, "password": password}

def test_user_login_success(registered_user):
    """
    TC003: Verify that a registered user can log in and receive a JWT token.
    """
    # 1. Provide valid credentials
    login_payload = {
        "username": registered_user["username"],
        "password": registered_user["password"]
    }

    # 2. Submit login request
    response = requests.post(f"{BASE_URL}/login", json=login_payload)

    # Expected Result: Login successful
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
    
    # Expected Result: Access token is returned
    data = response.json()
    assert "access_token" in data, "Response body does not contain 'access_token'"
    assert isinstance(data["access_token"], str), "Access token should be a string"
    assert len(data["access_token"]) > 0, "Access token is empty"