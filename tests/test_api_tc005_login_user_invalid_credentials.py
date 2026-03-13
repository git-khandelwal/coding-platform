import pytest
import requests

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def valid_login_credentials():
    # These are the valid credentials for the test user
    return {"username": "test", "password": "1234"}

@pytest.fixture(scope="module", autouse=True)
def ensure_test_user_exists(valid_login_credentials):
    # Register the user if not already registered
    url = f"{BASE_URL}/register"
    resp = requests.post(url, json=valid_login_credentials)
    # If user already exists, that's fine; ignore error
    yield
    # No teardown needed

def test_login_invalid_username(valid_login_credentials):
    """
    TC005 Step 1: Send login request with incorrect username.
    Expect 401 Unauthorized and error message.
    """
    payload = {
        "username": "wronguser",
        "password": valid_login_credentials["password"]
    }
    url = f"{BASE_URL}/login"
    resp = requests.post(url, json=payload)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
    data = resp.json()
    assert "error" in data, "Expected 'error' in response"
    assert data["error"] == "Invalid username or password", f"Unexpected error message: {data['error']}"

def test_login_invalid_password(valid_login_credentials):
    """
    TC005 Step 2: Send login request with incorrect password.
    Expect 401 Unauthorized and error message.
    """
    payload = {
        "username": valid_login_credentials["username"],
        "password": "wrongpassword"
    }
    url = f"{BASE_URL}/login"
    resp = requests.post(url, json=payload)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
    data = resp.json()
    assert "error" in data, "Expected 'error' in response"
    assert data["error"] == "Invalid username or password", f"Unexpected error message: {data['error']}"