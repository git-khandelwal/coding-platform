import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def test_user():
    # Generate a unique username for isolation
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "TestPassword123!"
    # Register the user
    resp = requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
    assert resp.status_code == 201
    yield {"username": username, "password": password}
    # No teardown endpoint for user deletion; if available, add cleanup here

@pytest.fixture(scope="module")
def auth_token(test_user):
    # Login and get JWT token
    resp = requests.post(f"{BASE_URL}/login", json={"username": test_user["username"], "password": test_user["password"]})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    return data["access_token"]

@pytest.fixture(scope="module")
def problem_id(auth_token):
    # Create a new problem to ensure it exists
    headers = {"Authorization": f"Bearer {auth_token}"}
    problem_data = {
        "title": "Sample Problem",
        "description": "Sample description",
        "difficulty": "Easy",
        "input_format": "int n",
        "output_format": "int",
        "sample_input": "1",
        "sample_output": "1",
        "sample_code": "def solve(n):\n    return n",
        "constraints": "1 <= n <= 1000"
    }
    resp = requests.post(f"{BASE_URL}/problems/add", json=problem_data, headers=headers)
    assert resp.status_code in (200, 201)
    # Try to extract problem id from response
    data = resp.json()
    if "problem" in data and "id" in data["problem"]:
        pid = data["problem"]["id"]
    elif "id" in data:
        pid = data["id"]
    else:
        # Fallback: get list of problems and find the one we just created
        list_resp = requests.get(f"{BASE_URL}/problems")
        assert list_resp.status_code == 200
        problems = list_resp.json()
        pid = None
        for p in problems:
            if p.get("title") == problem_data["title"]:
                pid = p.get("id")
                break
        assert pid is not None, "Could not determine problem ID"
    return pid

@pytest.fixture(scope="module")
def make_submission(auth_token, problem_id):
    # Submit a solution so that submission history is not empty
    headers = {"Authorization": f"Bearer {auth_token}"}
    code = "def solve(n):\n    return n"
    resp = requests.post(
        f"{BASE_URL}/problems/{problem_id}/solve",
        json={"code": code},
        headers=headers
    )
    assert resp.status_code == 200
    yield
    # No teardown for submissions

def test_get_submission_history_authenticated(auth_token, problem_id, make_submission):
    """
    TC020: Get Submission History (Authenticated)
    Steps:
      1. Register and login to get token.
      2. Send GET request to retrieve submissions for a problem with Authorization header.
    Expected:
      1. Response status is 200 OK.
      2. Response contains an array of submission objects.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = requests.get(f"{BASE_URL}/problems/{problem_id}/submissions", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    for submission in data:
        assert isinstance(submission, dict)
        assert "problem_title" in submission
        assert "status" in submission
        assert "result" in submission
        assert "timestamp" in submission
        assert "code" in submission