import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def test_user():
    username = f"testuser_tc027_{uuid.uuid4().hex[:8]}"
    password = "TestPassword123!"
    # Register user
    resp = requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
    assert resp.status_code in (200, 201)
    yield {"username": username, "password": password}
    # No teardown for user (assumed not needed)

@pytest.fixture(scope="module")
def auth_token(test_user):
    resp = requests.post(f"{BASE_URL}/login", json={"username": test_user["username"], "password": test_user["password"]})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    return data["access_token"]

@pytest.fixture
def created_problem(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    problem_data = {
        "title": "TC027 Problem",
        "description": "Edit/Delete test problem",
        "difficulty": "Easy",
        "input_format": "1 integer",
        "output_format": "1 integer",
        "sample_input": "1",
        "sample_output": "1",
        "sample_code": "def foo(x): return x",
        "constraints": "1 <= x <= 100"
    }
    resp = requests.post(f"{BASE_URL}/problems/add", json=problem_data, headers=headers)
    assert resp.status_code in (200, 201)
    # Try to get problem id from response, else fetch from list
    try:
        problem = resp.json().get("problem")
        if problem and "id" in problem:
            problem_id = problem["id"]
        else:
            raise Exception
    except Exception:
        # Fallback: find by title
        resp_list = requests.get(f"{BASE_URL}/problems")
        assert resp_list.status_code == 200
        problems = resp_list.json() if resp_list.headers.get("Content-Type", "").startswith("application/json") else []
        problem_id = None
        for p in problems:
            if p.get("title") == problem_data["title"]:
                problem_id = p.get("id")
                break
        assert problem_id is not None, "Could not find created problem in list"
    yield problem_id
    # Teardown: ensure problem is deleted if still exists
    requests.delete(f"{BASE_URL}/problems/{problem_id}", headers=headers)

def test_tc027_edit_and_delete_problem_as_authenticated_user(auth_token, created_problem):
    headers = {"Authorization": f"Bearer {auth_token}"}
    problem_id = created_problem

    # Step 2: Navigate to problem details page (GET)
    resp = requests.get(f"{BASE_URL}/problems/{problem_id}", headers=headers)
    assert resp.status_code == 200 or resp.status_code == 302  # Accept HTML or redirect
    # Cannot assert on "edit/delete options" in API, but endpoint is accessible

    # Step 3: Edit problem details and save (PUT)
    updated_data = {
        "title": "TC027 Problem Edited",
        "description": "Edited description",
        "difficulty": "Medium",
        "input_format": "2 integers",
        "output_format": "1 integer",
        "sample_input": "2 3",
        "sample_output": "5",
        "sample_code": "def foo(x, y): return x+y",
        "constraints": "1 <= x, y <= 100"
    }
    resp = requests.put(f"{BASE_URL}/problems/{problem_id}", json=updated_data, headers=headers)
    assert resp.status_code == 200
    assert resp.json().get("message") == "Problem updated successfully"

    # Verify update (GET)
    resp = requests.get(f"{BASE_URL}/problems/{problem_id}", headers=headers)
    assert resp.status_code == 200 or resp.status_code == 302
    # If JSON, check fields; if HTML, skip content check
    if resp.headers.get("Content-Type", "").startswith("application/json"):
        data = resp.json()
        assert data.get("title") == updated_data["title"]
        assert data.get("description") == updated_data["description"]

    # Step 4: Delete problem (DELETE)
    resp = requests.delete(f"{BASE_URL}/problems/{problem_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json().get("message") == "Problem deleted successfully"

    # Step 5: Verify problem is removed from list
    resp = requests.get(f"{BASE_URL}/problems", headers=headers)
    assert resp.status_code == 200
    problems = resp.json() if resp.headers.get("Content-Type", "").startswith("application/json") else []
    for p in problems:
        assert p.get("id") != problem_id