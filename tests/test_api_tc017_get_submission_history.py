import pytest
import requests

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def test_user_credentials():
    # These should be unique for each test run if the backend requires unique usernames
    return {
        "username": "testuser_tc017",
        "password": "TestPass123!"
    }

@pytest.fixture(scope="module")
def jwt_token(test_user_credentials):
    # Register user
    reg_resp = requests.post(f"{BASE_URL}/register", json=test_user_credentials)
    # Registration may fail if user already exists; that's fine for login
    # Log in to get JWT token
    login_resp = requests.post(f"{BASE_URL}/login", json=test_user_credentials)
    assert login_resp.status_code == 200, "Login failed for test user"
    data = login_resp.json()
    assert "access_token" in data, "No access_token in login response"
    return data["access_token"]

@pytest.fixture(scope="module")
def problem_id(jwt_token):
    # Create a problem so we have a valid problem_id
    problem_data = {
        "title": "TC017 Problem",
        "description": "Test problem for TC017",
        "difficulty": "Easy",
        "input_format": "int n",
        "output_format": "int",
        "sample_input": "2",
        "sample_output": "4",
        "sample_code": "def solve(n): return n*2",
        "constraints": "1 <= n <= 100"
    }
    headers = {"Authorization": f"Bearer {jwt_token}"}
    resp = requests.post(f"{BASE_URL}/problems/add", json=problem_data, headers=headers)
    assert resp.status_code == 201, "Problem creation failed"
    resp_json = resp.json()
    # The response should contain the problem object
    problem = resp_json.get("problem")
    assert problem and "id" in problem, "No problem ID in add problem response"
    return problem["id"]

@pytest.fixture(scope="module")
def create_submission(jwt_token, problem_id):
    # Submit a solution so there is at least one submission in the history
    headers = {"Authorization": f"Bearer {jwt_token}"}
    submission_data = {
        "code": "def solve(n): return n*2"
    }
    resp = requests.post(f"{BASE_URL}/problems/{problem_id}/solve", json=submission_data, headers=headers)
    assert resp.status_code == 200, "Submission failed"
    return True

def test_get_submission_history_authenticated(jwt_token, problem_id, create_submission):
    """
    TC017: Verify that an authenticated user can retrieve submission history for a problem.
    """
    headers = {"Authorization": f"Bearer {jwt_token}"}
    resp = requests.get(f"{BASE_URL}/problems/{problem_id}/submissions", headers=headers)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    submissions = resp.json()
    assert isinstance(submissions, list), "Response is not a list"
    # Each submission should be a dict with expected keys
    if submissions:
        for submission in submissions:
            assert isinstance(submission, dict), "Submission item is not a dict"
            assert "problem_title" in submission, "Missing 'problem_title' in submission"
            assert "status" in submission, "Missing 'status' in submission"
            assert "result" in submission, "Missing 'result' in submission"
            assert "timestamp" in submission, "Missing 'timestamp' in submission"
            assert "code" in submission, "Missing 'code' in submission"