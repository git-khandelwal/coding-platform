import pytest
import requests

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def test_user():
    # Register a user (ignore if already exists)
    username = "tc025_user"
    password = "tc025_password"
    try:
        resp = requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
        assert resp.status_code in (200, 201, 400)
    except Exception:
        pass
    return {"username": username, "password": password}

@pytest.fixture(scope="module")
def auth_token(test_user):
    resp = requests.post(f"{BASE_URL}/login", json={"username": test_user["username"], "password": test_user["password"]})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    return data["access_token"]

@pytest.fixture(scope="module")
def problem_id(auth_token):
    # Add a problem to solve
    headers = {"Authorization": f"Bearer {auth_token}"}
    problem_data = {
        "title": "Sum Two Numbers",
        "description": "Return the sum of two numbers.",
        "difficulty": "Easy",
        "input_format": "Two integers a and b",
        "output_format": "Single integer, the sum",
        "sample_input": "2 3",
        "sample_output": "5",
        "sample_code": "def solve(a, b):\n    return a + b",
        "constraints": "1 <= a, b <= 100"
    }
    resp = requests.post(f"{BASE_URL}/problems/add", json=problem_data, headers=headers)
    assert resp.status_code in (200, 201)
    # Try to extract problem id from response, fallback to listing problems
    if "problem" in resp.json():
        # Some APIs echo back the created object with an id
        created = resp.json()["problem"]
        if "id" in created:
            return created["id"]
    # Otherwise, get the latest problem
    resp = requests.get(f"{BASE_URL}/problems")
    assert resp.status_code == 200
    # This endpoint likely returns HTML, so we cannot reliably parse for id
    # Instead, try to get the problem list from API if available
    # If not possible, note the gap
    pytest.skip("Cannot reliably retrieve problem_id from /problems endpoint response. Test cannot proceed.")

@pytest.fixture(scope="function")
def code_to_submit():
    # Code that should pass for the sample problem
    return "def solve(a, b):\n    return a + b"

def test_tc025_solve_problem_and_submit_solution(auth_token, problem_id, code_to_submit):
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Step 2: Navigate to problem solve page (GET /problems/<id>/solve)
    resp = requests.get(f"{BASE_URL}/problems/{problem_id}/solve", headers=headers)
    assert resp.status_code == 200
    # Since this returns HTML, check for code editor presence in response text
    assert "textarea" in resp.text or "editor" in resp.text.lower() or "code" in resp.text.lower()

    # Step 3 & 4: Enter code in editor and submit solution (POST /problems/<id>/solve)
    payload = {"code": code_to_submit}
    resp = requests.post(f"{BASE_URL}/problems/{problem_id}/solve", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "result" in data
    assert data["message"] == "Submission evaluated"
    # Step 5: View evaluation result
    # At least one of status/result must be non-empty
    assert data["status"] in ("Success", "Failed", "Error", "Pending")
    assert isinstance(data["result"], str)
    # Expected Result: Submission is evaluated and result is displayed
    assert data["result"] != ""