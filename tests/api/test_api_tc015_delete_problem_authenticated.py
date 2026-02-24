import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def test_user():
    # Generate a unique username for isolation
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "TestPassword123!"
    yield {"username": username, "password": password}

@pytest.fixture(scope="module")
def access_token(test_user):
    # Register user
    reg_resp = requests.post(
        f"{BASE_URL}/register",
        json={"username": test_user["username"], "password": test_user["password"]}
    )
    assert reg_resp.status_code == 201

    # Login user
    login_resp = requests.post(
        f"{BASE_URL}/login",
        json={"username": test_user["username"], "password": test_user["password"]}
    )
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "access_token" in data
    return data["access_token"]

@pytest.fixture
def created_problem_id(access_token):
    # Add a new problem to ensure it exists for deletion
    problem_data = {
        "title": "Sample Problem for Deletion",
        "description": "Delete me!",
        "difficulty": "Easy",
        "input_format": "int n",
        "output_format": "int",
        "sample_input": "1",
        "sample_output": "1",
        "sample_code": "def solve(n): return n",
        "constraints": "1 <= n <= 10"
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.post(f"{BASE_URL}/problems/add", json=problem_data, headers=headers)
    assert resp.status_code == 201
    resp_json = resp.json()
    # Try to extract problem ID from response
    problem_id = resp_json.get("id")
    if not problem_id:
        # If not present, fetch all problems and find the one we just created
        list_resp = requests.get(f"{BASE_URL}/problems")
        assert list_resp.status_code == 200
        problems = list_resp.json()
        # Find by title and description
        for p in problems:
            if p.get("title") == problem_data["title"] and p.get("description") == problem_data["description"]:
                problem_id = p.get("id")
                break
    assert problem_id is not None, "Could not determine created problem ID"
    yield problem_id
    # Teardown: nothing to do, as the test will delete it

def test_delete_problem_authenticated(access_token, created_problem_id):
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.delete(f"{BASE_URL}/problems/{created_problem_id}", headers=headers)
    assert resp.status_code == 200
    resp_json = resp.json()
    assert "message" in resp_json
    assert resp_json["message"] == "Problem deleted successfully"