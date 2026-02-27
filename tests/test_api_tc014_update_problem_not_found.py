import pytest
import requests

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def test_user_credentials():
    # These should match a valid user in the test DB or registration endpoint
    return {
        "username": "tc014user",
        "password": "tc014password"
    }

@pytest.fixture(scope="module")
def jwt_token(test_user_credentials):
    # Register user (ignore errors if already exists)
    requests.post(f"{BASE_URL}/register", json=test_user_credentials)
    # Log in to get JWT token
    login_resp = requests.post(f"{BASE_URL}/login", json=test_user_credentials)
    assert login_resp.status_code == 200, "Login failed, cannot obtain JWT token"
    token = login_resp.json().get("access_token")
    assert token, "No access_token in login response"
    return token

@pytest.fixture
def invalid_problem_id():
    # Use a high number unlikely to exist in the test DB
    return 999999

def test_update_nonexistent_problem_returns_404(jwt_token, invalid_problem_id):
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    update_data = {
        "title": "Updated Title",
        "description": "Updated Description"
    }
    resp = requests.put(f"{BASE_URL}/problems/{invalid_problem_id}", json=update_data, headers=headers)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"