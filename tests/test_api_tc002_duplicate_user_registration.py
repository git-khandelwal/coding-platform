import pytest
import requests

# NOTE: The base URL is assumed to be provided via environment or configuration.
# If not available, it defaults to localhost:5000.
BASE_URL = "http://localhost:5000"

@pytest.fixture
def user_credentials():
    return {
        "username": "testuser_unique_123",
        "password": "securepassword123"
    }

def test_duplicate_user_registration(user_credentials):
    """
    TC002: Verify that registration fails when using an existing username.
    """
    register_url = f"{BASE_URL}/register"
    
    # 1. Register a user
    response_first = requests.post(register_url, json=user_credentials)
    assert response_first.status_code == 201, "Initial registration failed"

    # 2. Attempt to register again with the same username
    response_second = requests.post(register_url, json=user_credentials)

    # Expected Result: 400 Bad Request error returned
    assert response_second.status_code == 400, "Expected 400 Bad Request for duplicate registration"
    
    # Verify error message content
    data = response_second.json()
    assert "error" in data
    assert data["error"] == "Username already exists"

    # Teardown logic: In a real environment, one would delete the user from the DB here.
    # Since no DB cleanup utility was provided in the context, this is noted as a requirement 
    # for a production-grade test suite.