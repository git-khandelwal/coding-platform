import pytest
import requests
import time
from datetime import datetime, timedelta

# NOTE: The test case requires waiting for 3 hours. 
# In a real-world CI/CD pipeline, waiting 3 hours is impractical.
# This script assumes the existence of a mechanism to manipulate time or 
# that the environment allows for a mock configuration of the JWT expiration.
# If no such mechanism exists, this test cannot be executed as written.

BASE_URL = "http://localhost:5000"

@pytest.fixture
def registered_user():
    user_data = {"username": "testuser_tc010", "password": "securepassword123"}
    requests.post(f"{BASE_URL}/register", json=user_data)
    return user_data

@pytest.fixture
def auth_token(registered_user):
    response = requests.post(f"{BASE_URL}/login", json=registered_user)
    assert response.status_code == 200
    return response.json().get("access_token")

def test_jwt_token_expiration(auth_token):
    """
    TC010: Verify that protected endpoints reject requests after the 3-hour token validity period.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Step 1: Verify token is valid initially
    initial_response = requests.get(f"{BASE_URL}/protected", headers=headers)
    assert initial_response.status_code == 200, "Token should be valid initially"

    # Step 2: Wait for 3 hours
    # CRITICAL GAP: Waiting 3 hours in a test script is not feasible.
    # In a production-grade test suite, we would use a time-travel mock or 
    # configure the JWT_ACCESS_TOKEN_EXPIRES to a shorter duration (e.g., 1 second) for testing.
    print("Waiting for 3 hours token expiration...")
    time.sleep(3 * 60 * 60 + 10) 

    # Step 3: Access protected endpoint
    expired_response = requests.get(f"{BASE_URL}/protected", headers=headers)

    # Expected Result: 401 Unauthorized
    assert expired_response.status_code == 401, f"Expected 401, got {expired_response.status_code}"
    assert "msg" in expired_response.json() or "error" in expired_response.json()