import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def user_credentials():
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "TestPassword123!"
    return {"username": username, "password": password}

@pytest.fixture(scope="module")
def auth_token(user_credentials):
    # Register user
    register_resp = requests.post(f"{BASE_URL}/register", json=user_credentials)
    assert register_resp.status_code == 201

    # Login user
    login_resp = requests.post(f"{BASE_URL}/login", json=user_credentials)
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "access_token" in data
    return data["access_token"]

def test_update_nonexistent_problem_returns_404(auth_token):
    # Use a high, unlikely-to-exist problem ID
    non_existent_problem_id = 999999
    update_data = {
        "title": "Updated Title",
        "description": "Updated Description",
        "difficulty": "Medium",
        "input_format": "int n",
        "output_format": "int result",
        "sample_input": "1",
        "sample_output": "2",
        "sample_code": "print(2)",
        "constraints": "1 <= n <= 1000"
    }
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    response = requests.put(
        f"{BASE_URL}/problems/{non_existent_problem_id}",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 404