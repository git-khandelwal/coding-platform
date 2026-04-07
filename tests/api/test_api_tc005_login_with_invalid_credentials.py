import pytest
import requests

# Gaps in information:
# - The base URL of the API is not provided.
# Please set the BASE_URL environment variable or replace the value below with the correct API URL.
BASE_URL = "http://localhost:5000"  # <-- Replace with actual API base URL if different

@pytest.fixture(scope="module")
def login_url():
    return f"{BASE_URL}/login"

def test_login_with_invalid_credentials(login_url):
    """
    TC005: Login with Invalid Credentials
    Test logging in with incorrect username or password.
    Expected:
      - Response status is 401 Unauthorized.
      - Response contains "Invalid username or password".
    """
    payload = {
        "username": "nonexistent_user",
        "password": "wrongpassword"
    }
    response = requests.post(login_url, json=payload)
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
    response_json = response.json()
    assert "error" in response_json, "Expected 'error' key in response"
    assert "Invalid username or password" in response_json["error"], (
        f"Expected error message to contain 'Invalid username or password', got '{response_json['error']}'"
    )