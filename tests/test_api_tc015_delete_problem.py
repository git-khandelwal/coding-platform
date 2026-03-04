import pytest
import requests

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def test_user_credentials():
    # These should be unique for test isolation in a real environment
    return {
        "username": "testuser_tc015",
        "password": "TestPassword123!"
    }

@pytest.fixture(scope="module")
def auth_token(test_user_credentials):
    # Register the user (ignore if already exists)
    reg_resp = requests.post(
        f"{BASE_URL}/register",
        json={
            "username": test_user_credentials["username"],
            "password": test_user_credentials["password"]
        }
    )
    # Login to get JWT token
    login_resp = requests.post(
        f"{BASE_URL}/login",
        json={
            "username": test_user_credentials["username"],
            "password": test_user_credentials["password"]
        }
    )
    assert login_resp.status_code == 200, "Login failed for test user"
    token = login_resp.json().get("access_token")
    assert token, "No access_token in login response"
    return token

@pytest.fixture
def created_problem_id(auth_token):
    # Create a problem to ensure it exists for deletion
    headers = {"Authorization": f"Bearer {auth_token}"}
    problem_data = {
        "title": "TC015 Problem",
        "description": "A problem to be deleted in TC015.",
        "difficulty": "Easy",
        "input_format": "int n",
        "output_format": "int result",
        "sample_input": "1",
        "sample_output": "1",
        "sample_code": "def solve(n): return n",
        "constraints": "1 <= n <= 100"
    }
    resp = requests.post(f"{BASE_URL}/problems/add", json=problem_data, headers=headers)
    assert resp.status_code == 201, "Failed to create problem for deletion"
    # Try to extract problem ID from response
    resp_json = resp.json()
    problem_id = None
    if isinstance(resp_json, dict):
        # Try common keys
        if "problem" in resp_json and isinstance(resp_json["problem"], dict):
            problem_id = resp_json["problem"].get("id")
        elif "id" in resp_json:
            problem_id = resp_json["id"]
    if not problem_id:
        # Fallback: fetch problems and find by title
        get_resp = requests.get(f"{BASE_URL}/problems")
        assert get_resp.status_code == 200, "Cannot fetch problems list"
        problems = get_resp.json()
        for p in problems:
            if p.get("title") == "TC015 Problem":
                problem_id = p.get("id")
                break
    assert problem_id, "Could not determine created problem ID"
    yield problem_id
    # Teardown: Ensure the problem is deleted (ignore errors)
    requests.delete(f"{BASE_URL}/problems/{problem_id}", headers=headers)

def test_tc015_delete_problem(auth_token, created_problem_id):
    """
    TC015: Verify that an authenticated user can delete an existing problem.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = requests.delete(f"{BASE_URL}/problems/{created_problem_id}", headers=headers)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    resp_json = resp.json()
    assert "Problem deleted successfully" in resp_json.get("message", ""), "Success message missing in response"