# Developed By John Wick
import requests
import pytest

BASE_URL = "http://localhost:5000"

@pytest.fixture
def credentials():
    """Return valid user credentials for authentication."""
    return {"username": "testuser", "password": "testpass"}

@pytest.fixture
def access_token(credentials):
    """Authenticate and return a valid JWT access token."""
    login_url = f"{BASE_URL}/login"
    response = requests.post(login_url, json=credentials)
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "access_token" in data, "No access_token in login response"
    return data["access_token"]

def test_access_protected_endpoint_with_valid_token(access_token, credentials):
    """Test that a GET request to the protected endpoint with a valid JWT returns user information."""
    protected_url = f"{BASE_URL}/protected"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(protected_url, headers=headers)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    data = response.json()
    assert "logged_in_as" in data, "Response missing 'logged_in_as'"
    assert data["logged_in_as"] == credentials["username"], (
        f"Expected logged_in_as to be '{credentials['username']}', got '{data['logged_in_as']}'"
    )