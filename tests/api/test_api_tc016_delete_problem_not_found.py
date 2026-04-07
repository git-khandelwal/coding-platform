import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def test_user():
    """
    Registers a new user and returns the username and password.
    """
    username = f"testuser_tc016_{uuid.uuid4().hex[:8]}"
    password = "TestPassword123!"
    register_url = f"{BASE_URL}/register"
    payload = {"username": username, "password": password}
    resp = requests.post(register_url, json=payload)
    # Registration may succeed or user may already exist; ignore for this test
    return {"username": username, "password": password}

@pytest.fixture(scope="module")
def access_token(test_user):
    """
    Logs in with the test user and returns the JWT access token.
    """
    login_url = f"{BASE_URL}/login"
    payload = {"username": test_user["username"], "password": test_user["password"]}
    resp = requests.post(login_url, json=payload)
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    data = resp.json()
    assert "access_token" in data, "No access_token in login response"
    return data["access_token"]

@pytest.fixture
def auth_header(access_token):
    return {"Authorization": f"Bearer {access_token}"}

def test_delete_problem_not_found(auth_header):
    """
    TC016: Test deleting a non-existent problem.
    Steps:
    1. Register and login to get token.
    2. Send DELETE request for a non-existent problem ID.
    Expected:
    1. Response status is 404 Not Found.
    """
    # Use a high, unlikely-to-exist problem ID
    non_existent_problem_id = 999999
    delete_url = f"{BASE_URL}/problems/{non_existent_problem_id}"
    resp = requests.delete(delete_url, headers=auth_header)
    assert resp.status_code == 404, f"Expected 404 Not Found, got {resp.status_code} with body: {resp.text}"