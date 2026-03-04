import pytest
import requests

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def test_user_credentials():
    # These should be unique per test run if user registration is required
    return {
        "username": "testuser_tc011",
        "password": "TestPass123!"
    }

@pytest.fixture(scope="module")
def jwt_token(test_user_credentials):
    # Register user (ignore if already exists)
    reg_resp = requests.post(
        f"{BASE_URL}/register",
        json={
            "username": test_user_credentials["username"],
            "password": test_user_credentials["password"]
        }
    )
    # Registration may fail if user already exists; that's fine for login

    # Login to get JWT token
    login_resp = requests.post(
        f"{BASE_URL}/login",
        json={
            "username": test_user_credentials["username"],
            "password": test_user_credentials["password"]
        }
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    data = login_resp.json()
    assert "access_token" in data, "No access_token in login response"
    return data["access_token"]

@pytest.fixture
def valid_problem_data():
    return {
        "title": "Sum of Two Numbers",
        "description": "Given two integers, return their sum.",
        "difficulty": "Easy",
        "input_format": "Two integers a and b",
        "output_format": "Single integer, the sum of a and b",
        "sample_input": "2 3",
        "sample_output": "5",
        "sample_code": "def sum_two(a, b): return a + b",
        "constraints": "1 <= a, b <= 1000"
    }

def test_tc011_add_problem_authenticated(jwt_token, valid_problem_data):
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    resp = requests.post(
        f"{BASE_URL}/problems/add",
        json=valid_problem_data,
        headers=headers
    )
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    resp_json = resp.json()
    assert "message" in resp_json, "No 'message' in response"
    assert resp_json["message"] == "Problem added successfully", f"Unexpected message: {resp_json['message']}"
    assert "problem" in resp_json, "No 'problem' in response"
    # Optionally check that returned problem matches sent data
    for key in valid_problem_data:
        assert resp_json["problem"].get(key) == valid_problem_data[key], f"Mismatch in field '{key}'"