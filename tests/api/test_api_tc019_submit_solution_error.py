import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def test_user():
    """
    Registers and logs in a new user, returns (username, password, access_token).
    """
    username = f"testuser_tc019_{uuid.uuid4().hex[:8]}"
    password = "TestPassword123!"
    register_resp = requests.post(
        f"{BASE_URL}/register",
        json={"username": username, "password": password},
    )
    assert register_resp.status_code == 201 or register_resp.status_code == 200

    login_resp = requests.post(
        f"{BASE_URL}/login",
        json={"username": username, "password": password},
    )
    assert login_resp.status_code == 200
    token = login_resp.json().get("access_token")
    assert token is not None
    return username, password, token

@pytest.fixture(scope="module")
def problem_id(test_user):
    """
    Creates a new problem and returns its ID.
    """
    _, _, token = test_user
    problem_data = {
        "title": "TC019 Problem",
        "description": "Test problem for TC019",
        "difficulty": "Easy",
        "input_format": "N/A",
        "output_format": "N/A",
        "sample_input": "",
        "sample_output": "",
        "sample_code": "",
        "constraints": "",
    }
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{BASE_URL}/problems/add", json=problem_data, headers=headers)
    assert resp.status_code == 201 or resp.status_code == 200
    # Try to get problem ID from response, else fetch problems and find it
    try:
        resp_json = resp.json()
        pid = resp_json.get("id")
        if pid:
            return pid
    except Exception:
        pass
    # Fallback: fetch all problems and find by title
    problems_resp = requests.get(f"{BASE_URL}/problems")
    assert problems_resp.status_code == 200
    problems = problems_resp.json()
    for p in problems:
        if p.get("title") == problem_data["title"]:
            return p.get("id")
    pytest.fail("Could not determine problem ID for TC019 test.")

def test_tc019_submit_solution_with_error(test_user, problem_id):
    """
    TC019: Submit Solution (Error)
    1. Register and login to get token.
    2. Send POST request to submit code with error for a problem with Authorization header.
    Expected:
    - Response status is 200 OK.
    - Response contains "Submission evaluated" with status "Error" and error message.
    """
    _, _, token = test_user
    headers = {"Authorization": f"Bearer {token}"}
    # Example code with syntax error
    code_with_error = "def solution()\n    return 42"
    payload = {"code": code_with_error}
    resp = requests.post(
        f"{BASE_URL}/problems/{problem_id}/solve",
        json=payload,
        headers=headers,
    )
    assert resp.status_code == 200
    resp_json = resp.json()
    assert "message" in resp_json
    assert resp_json["message"] == "Submission evaluated"
    assert "status" in resp_json
    assert resp_json["status"] == "Error"
    assert "result" in resp_json
    assert isinstance(resp_json["result"], str)
    assert resp_json["result"] != ""
    # Optionally check for presence of error message keywords
    assert "error" in resp_json["result"].lower() or "exception" in resp_json["result"].lower() or "syntax" in resp_json["result"].lower()