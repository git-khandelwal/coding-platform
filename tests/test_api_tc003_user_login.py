import pytest
import requests

# NOTE: The base URL is not provided in the context. 
# Assuming a default local development URL.
BASE_URL = "http://localhost:5000"

@pytest.fixture
def valid_user_credentials():
    """
    Provides valid credentials for the login test.
    NOTE: The system requires a pre-existing user in the database.
    If the environment is clean, a registration step would be required here.
    """
    return {
        "username": "testuser",
        "password": "testpassword123"
    }

def test_user_login_success(valid_user_credentials):
    """
    TC003: Verify authenticated access using valid credentials.
    Steps:
    1. Enter valid username and password.
    2. Submit login.
    Expected Result: System returns JWT access token.
    """
    login_url = f"{BASE_URL}/login"
    
    response = requests.post(login_url, json=valid_user_credentials)
    
    # Assert successful status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    # Assert response contains access_token
    data = response.json()
    assert "access_token" in data, "Response body does not contain 'access_token'"
    assert isinstance(data["access_token"], str), "Access token should be a string"
    assert len(data["access_token"]) > 0, "Access token should not be empty"