import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def test_user_credentials():
    # Generate a unique username for isolation
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "TestPassword123!"
    return {"username": username, "password": password}

@pytest.fixture(scope="module")
def register_and_login_user(test_user_credentials):
    # Register the user
    register_resp = requests.post(
        f"{BASE_URL}/register",
        json={
            "username": test_user_credentials["username"],
            "password": test_user_credentials["password"]
        }
    )
    # Registration may fail if user already exists, but for isolation we use a unique username
    assert register_resp.status_code == 201
    # Login to get JWT token
    login_resp = requests.post(
        f"{BASE_URL}/login",
        json={
            "username": test_user_credentials["username"],
            "password": test_user_credentials["password"]
        }
    )
    assert login_resp.status_code == 200
    token = login_resp.json().get("access_token")
    assert token is not None
    return {
        "username": test_user_credentials["username"],
        "token": token
    }

def test_access_protected_with_valid_token(register_and_login_user):
    """
    TC006: Verify access to protected endpoint with a valid JWT token.
    Steps:
      1. Log in to obtain JWT token.
      2. Send GET request to protected endpoint with token.
    Expected Result:
      1. Response status is 200.
      2. Response contains "logged_in_as" with username.
    """
    token = register_and_login_user["token"]
    username = register_and_login_user["username"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    resp = requests.get(f"{BASE_URL}/protected", headers=headers)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}, body: {resp.text}"
    json_data = resp.json()
    assert "logged_in_as" in json_data, f"Response JSON missing 'logged_in_as': {json_data}"
    assert json_data["logged_in_as"] == username, f"Expected username '{username}', got '{json_data['logged_in_as']}'"