import pytest
import requests

# NOTE: The base URL is not provided in the context. 
# Assuming a standard local development environment.
BASE_URL = "http://localhost:5000"

@pytest.fixture
def login_url():
    return f"{BASE_URL}/login"

def test_invalid_login_returns_401(login_url):
    """
    TC004: Verify that login fails with incorrect credentials.
    1. Provide invalid username or password.
    2. Submit login request.
    Expected: 401 Unauthorized error returned.
    """
    payload = {
        "username": "nonexistent_user",
        "password": "wrong_password"
    }
    
    response = requests.post(login_url, json=payload)
    
    assert response.status_code == 401, f"Expected 401, but got {response.status_code}"
    assert response.json().get("error") == "Invalid username or password"