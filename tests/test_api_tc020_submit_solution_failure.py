import pytest
import requests

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def test_user_credentials():
    # These should be valid credentials for an existing user
    # Gaps: Registration endpoint and user creation are not covered here.
    # If user does not exist, this test will fail.
    return {
        "username": "testuser_tc020",
        "password": "TestPassword123!"
    }

@pytest.fixture(scope="module")
def jwt_token(test_user_credentials):
    # Gaps: Registration flow is not included; assumes user already exists.
    login_url = f"{BASE_URL}/login"
    resp = requests.post(login_url, json=test_user_credentials)
    assert resp.status_code == 200, "Login failed, cannot obtain JWT token for TC020"
    data = resp.json()
    assert "access_token" in data, "No access_token in login response"
    return data["access_token"]

@pytest.fixture(scope="module")
def problem_id(jwt_token):
    # Gaps: No info on problem creation, assumes at least one problem exists with id=1.
    # If not, this fixture will fail.
    # Optionally, you could fetch the problems list and pick the first.
    problems_url = f"{BASE_URL}/problems"
    headers = {"Authorization": f"Bearer {jwt_token}"}
    resp = requests.get(problems_url, headers=headers)
    assert resp.status_code == 200, "Cannot fetch problems list for TC020"
    problems = resp.json()
    if isinstance(problems, list) and problems:
        return problems[0].get("id", 1)
    # Fallback to id=1 if problems list format is unknown
    return 1

def test_submit_solution_failure_tc020(jwt_token, problem_id):
    # Step 1: Log in to obtain JWT token (done via fixture)
    # Step 2: Send POST request to submit solution endpoint with incorrect code

    # Gaps: No info on problem signature, so we submit code that is likely incorrect for any problem.
    incorrect_code = "def solution(x):\n    return 0"

    submit_url = f"{BASE_URL}/problems/{problem_id}/solve"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "code": incorrect_code
    }
    resp = requests.post(submit_url, json=payload, headers=headers)
    assert resp.status_code == 200, f"Expected status 200, got {resp.status_code}"
    resp_json = resp.json()
    assert "status" in resp_json, "Response missing 'status' field"
    assert resp_json["status"] == "Failed", f"Expected status 'Failed', got '{resp_json['status']}'"