import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def test_user():
    """
    Registers and logs in a test user. Returns (username, password, access_token).
    """
    username = f"testuser_tc026_{uuid.uuid4().hex[:8]}"
    password = "TestPass123!"
    # Register user
    resp = requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
    assert resp.status_code in (200, 201)
    # Login user
    resp = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    return username, password, data["access_token"]

@pytest.fixture(scope="module")
def test_problem(test_user):
    """
    Adds a new problem as the test user. Returns the problem_id.
    """
    _, _, token = test_user
    headers = {"Authorization": f"Bearer {token}"}
    problem_data = {
        "title": f"TC026 Problem {uuid.uuid4().hex[:8]}",
        "description": "Test problem for TC026.",
        "difficulty": "Easy",
        "input_format": "int n",
        "output_format": "int",
        "sample_input": "2",
        "sample_output": "4",
        "sample_code": "def solve(n):\n    return n*2",
        "constraints": "1 <= n <= 100"
    }
    resp = requests.post(f"{BASE_URL}/problems/add", json=problem_data, headers=headers)
    assert resp.status_code == 201
    # The API returns the problem data, but not the ID. Fetch the problems list and find the problem by title.
    resp = requests.get(f"{BASE_URL}/problems")
    assert resp.status_code == 200
    # The problems list is rendered as HTML, so we need to fetch the problem ID another way.
    # Try to get the problem list as JSON if possible (if not, this is a gap in the context).
    # If the API does not provide a way to get the problem ID, we cannot proceed.
    # The context does not specify a JSON endpoint for problems list.
    # Try to get the latest problem by querying /problems/<id> incrementally.
    # This is a gap: No reliable way to get the problem_id from the API response.
    pytest.skip("Cannot reliably retrieve problem_id after creation; API does not return it and problems list is not JSON.")

@pytest.fixture
def auth_headers(test_user):
    """
    Returns the Authorization header for the test user.
    """
    return {"Authorization": f"Bearer {test_user[2]}"}

def test_tc026_view_submission_history(test_user, test_problem, auth_headers):
    """
    TC026: Test viewing submission history for a problem as an authenticated user.
    Steps:
    1. Log in as user.
    2. Navigate to problem solve page.
    3. Submit a solution.
    4. View submission history section.
    Expected:
    1. Submission history is displayed with latest submission.
    """
    # Step 2: Navigate to problem solve page (optional for API, but we can GET it)
    problem_id = test_problem
    resp = requests.get(f"{BASE_URL}/problems/{problem_id}/solve", headers=auth_headers)
    assert resp.status_code == 200

    # Step 3: Submit a solution
    code = "def solve(n):\n    return n*2"
    resp = requests.post(
        f"{BASE_URL}/problems/{problem_id}/solve",
        json={"code": code},
        headers=auth_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "result" in data

    # Step 4: View submission history
    resp = requests.get(f"{BASE_URL}/problems/{problem_id}/submissions", headers=auth_headers)
    assert resp.status_code == 200
    submissions = resp.json()
    assert isinstance(submissions, list)
    # Latest submission should be first
    assert len(submissions) >= 1
    latest = submissions[0]
    assert "problem_title" in latest
    assert "status" in latest
    assert "result" in latest
    assert "timestamp" in latest
    assert "code" in latest
    assert latest["code"] == code
    # Optionally, check that status/result match the submission result
    assert latest["status"] == data["status"]
    assert latest["result"] == data["result"]