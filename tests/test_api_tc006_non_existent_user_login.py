import pytest
import requests
import os

# NOTE: The base URL is assumed to be provided via environment variable or default to localhost
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")

@pytest.fixture
def login_url():
    return f"{BASE_URL}/login"

def test_non_existent_user_login(login_url):
    """
    TC006: Verify system rejects login for a username that does not exist.
    """
    # 1. Enter non-existent username and any password
    payload = {
        "username": "non_existent_user_xyz_123",
        "password": "some_password_123"
    }

    # 2. Submit login
    response = requests.post(login_url, json=payload)

    # Expected Result: System returns 401 Unauthorized error
    assert response.status_code == 401, f"Expected 401, but got {response.status_code}"
    
    # Optional: Verify error message content if applicable
    response_data = response.json()
    assert "error" in response_data
    assert response_data["error"] == "Invalid username or password"