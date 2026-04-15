import pytest
import requests
import os

# NOTE: The base URL is assumed to be provided via environment variable or default
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")

@pytest.fixture
def login_endpoint():
    return f"{BASE_URL}/login"

def test_empty_login_fields_returns_error(login_endpoint):
    """
    TC005: Verify system rejects login when fields are left blank.
    """
    # 1. Leave username and password blank
    payload = {
        "username": "",
        "password": ""
    }
    
    # 2. Submit login
    response = requests.post(login_endpoint, json=payload)
    
    # Expected Result: System returns error indicating fields are required or invalid.
    # Based on app/auth.py, the /login endpoint returns 401 for invalid credentials.
    # Note: The provided code context for /login does not explicitly check for empty strings
    # before querying the DB, so it will likely return a 401 "Invalid username or password".
    assert response.status_code == 401
    assert "error" in response.json()
    assert response.json()["error"] == "Invalid username or password"