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
    register_resp = requests.post(
        f"{BASE_URL}/register",
        json={
            "username": user_credentials["username"],
            "password": user_credentials["password"]
        }
    )
    # Registration may return 201 or 400 if user exists; ignore for idempotency

    # Login user
    login_resp = requests.post(
        f"{BASE_URL}/login",
        json={
            "username": user_credentials["username"],
            "password": user_credentials["password"]
        }
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json().get("access_token")
    assert token, "No access_token in login response"
    return token

@pytest.fixture
def valid_problem_data():
    return {
        "title": f"Sample Problem {uuid.uuid4().hex[:6]}",
        "description": "Solve the sample problem as described.",
        "difficulty": "Easy",
        "input_format": "A single integer n",
        "output_format": "The value of n squared",
        "sample_input": "2",
        "sample_output": "4",
        "sample_code": "print(int(input())**2)",
        "constraints": "1 <= n <= 1000"
    }

def test_add_new_problem_authenticated(auth_token, valid_problem_data):
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(
        f"{BASE_URL}/problems/add",
        json=valid_problem_data,
        headers=headers
    )

    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}: {response.text}"
    resp_json = response.json()
    assert "message" in resp_json, "No 'message' in response"
    assert resp_json["message"] == "Problem added successfully", f"Unexpected message: {resp_json['message']}"
    assert "problem" in resp_json, "No 'problem' in response"
    for key in valid_problem_data:
        assert resp_json["problem"].get(key) == valid_problem_data[key], f"Problem field '{key}' mismatch"