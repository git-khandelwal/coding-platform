import pytest
import requests

# NOTE: The base_url is assumed to be provided via environment or configuration.
# If not available, this script requires a constant or fixture to define the target API host.
BASE_URL = "http://localhost:5000"

@pytest.fixture
def valid_user_credentials():
    """
    Fixture providing a known valid username.
    Note: Password is intentionally incorrect for TC004.
    """
    return {
        "username": "testuser",
        "password": "incorrect_password_123"
    }

def test_login_with_invalid_credentials(valid_user_credentials):
    """
    TC004: Verify system rejects login with incorrect credentials.
    Steps:
    1. Enter valid username and incorrect password.
    2. Submit login.
    Expected Result: System returns 401 Unauthorized error.
    """
    login_url = f"{BASE_URL}/login"
    
    # Submit login request
    response = requests.post(login_url, json=valid_user_credentials)
    
    # Assertions based on Expected Result
    assert response.status_code == 401, f"Expected 401 Unauthorized, but got {response.status_code}"
    
    # Verify error message body
    data = response.json()
    assert "error" in data
    assert data["error"] == "Invalid username or password"