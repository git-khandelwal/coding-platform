import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def user_credentials():
    # Generate a unique username for isolation
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "TestPass123!"
    return {"username": username, "password": password}

@pytest.fixture(scope="module")
def auth_token(user_credentials):
    # Register user
    reg_resp = requests.post(
        f"{BASE_URL}/register",
        json={"username": user_credentials["username"], "password": user_credentials["password"]}
    )
    assert reg_resp.status_code in (200, 201), f"Registration failed: {reg_resp.text}"

    # Login user
    login_resp = requests.post(
        f"{BASE_URL}/login",
        json={"username": user_credentials["username"], "password": user_credentials["password"]}
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    data = login_resp.json()
    assert "access_token" in data, "No access_token in login response"
    return data["access_token"]

@pytest.fixture(scope="module")
def problem_id(auth_token):
    # Add a new problem so we know the ID and expected solution
    headers = {"Authorization": f"Bearer {auth_token}"}
    problem_data = {
        "title": "Sum Two Numbers",
        "description": "Return the sum of two numbers.",
        "difficulty": "Easy",
        "input_format": "Two integers, a and b",
        "output_format": "An integer, the sum of a and b",
        "sample_input": "2 3",
        "sample_output": "5",
        "sample_code": "def sum_two_numbers(a, b):\n    return a + b",
        "constraints": "1 <= a, b <= 1000"
    }
    resp = requests.post(f"{BASE_URL}/problems/add", json=problem_data, headers=headers)
    assert resp.status_code in (200, 201), f"Problem creation failed: {resp.text}"

    # Try to get the problem ID from response, fallback to listing problems
    try:
        resp_json = resp.json()
        if "id" in resp_json:
            return resp_json["id"]
    except Exception:
        pass

    # Fallback: get the latest problem from the list
    list_resp = requests.get(f"{BASE_URL}/problems")
    assert list_resp.status_code == 200, f"Problem listing failed: {list_resp.text}"
    problems = list_resp.json()
    # Find our problem by title
    for prob in problems:
        if prob.get("title") == problem_data["title"]:
            return prob.get("id")
    pytest.fail("Could not retrieve problem ID after creation.")

@pytest.fixture
def correct_code():
    # This code must match the expected function signature for the created problem
    return "def sum_two_numbers(a, b):\n    return a + b"

def test_TC017_submit_solution_success(auth_token, problem_id, correct_code):
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {
        "code": correct_code
    }
    resp = requests.post(
        f"{BASE_URL}/problems/{problem_id}/solve",
        json=payload,
        headers=headers
    )
    assert resp.status_code == 200, f"Expected 200 OK, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "message" in data, "Response missing 'message'"
    assert data["message"] == "Submission evaluated", f"Unexpected message: {data.get('message')}"
    assert data.get("status") == "Success", f"Expected status 'Success', got {data.get('status')}"
    assert data.get("result") == "Correct", f"Expected result 'Correct', got {data.get('result')}"