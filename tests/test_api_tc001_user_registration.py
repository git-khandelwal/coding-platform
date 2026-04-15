import pytest
import requests
import uuid

# NOTE: The base URL is missing from the provided context. 
# Assuming a standard local development environment for the API.
BASE_URL = "http://localhost:5000"

@pytest.fixture
def unique_user_data():
    """Generates unique credentials for user registration."""
    return {
        "username": f"testuser_{uuid.uuid4().hex[:8]}",
        "password": "SecurePassword123!"
    }

def test_user_registration_success(unique_user_data):
    """
    TC001: Verify that a new user can register with a unique username and password.
    Steps:
    1. Send POST request to /register with unique credentials.
    2. Verify response status code is 201.
    3. Verify success message in response body.
    """
    endpoint = f"{BASE_URL}/register"
    
    response = requests.post(endpoint, json=unique_user_data)
    
    # Assertions based on Expected Result
    assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.text}"
    
    response_data = response.json()
    assert response_data.get("message") == "User registered successfully"

    # Verification of user creation via login (optional but recommended for robustness)
    login_response = requests.post(f"{BASE_URL}/login", json=unique_user_data)
    assert login_response.status_code == 200, "User was not found in the system after registration"