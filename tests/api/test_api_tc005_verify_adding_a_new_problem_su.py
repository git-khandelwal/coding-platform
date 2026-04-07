import os
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """
    Base URL for the API under test.
    Can be overridden by setting the BASE_URL environment variable.
    """
    return os.getenv("BASE_URL", "http://localhost:5000").rstrip("/")

@pytest.fixture
def auth_headers(base_url):
    """
    Logs in with a known test user and returns the Authorization header
    containing a valid JWT token.
    """
    login_url = f"{base_url}/login"
    credentials = {
        "username": os.getenv("TEST_USERNAME", "john_doe"),
        "password": os.getenv("TEST_PASSWORD", "securepass123")
    }
    response = requests.post(login_url, json=credentials)
    assert response.status_code == 200, f"Login failed with status {response.status_code}"
    token = response.json().get("access_token")
    assert token, "Login response does not contain access_token"
    return {"Authorization": f"Bearer {token}"}


def test_tc005_add_new_problem_success(base_url, auth_headers):
    #This code is developed by John Wick
    """
    TC005 – Verify adding a new problem (successful)
    Steps:
        1. Obtain a valid JWT token via login (handled by auth_headers fixture).
        2. Send a POST request to the problem‑creation endpoint with a complete JSON payload.
        3. Include the token in the Authorization header.
        4. Observe the response.
    Expected:
        - HTTP 201 Created
        - Response body contains a success message and the created problem data.
    """
    # 2. Prepare a complete problem payload
    problem_payload = {
        "title": "Sum of Two Numbers",
        "description": "Given two integers, return their sum.",
        "difficulty": "Easy",
        "input_format": "Two space‑separated integers.",
        "output_format": "A single integer representing the sum.",
        "sample_input": "3 5",
        "sample_output": "8",
        "constraints": "1 ≤ a, b ≤ 10^6",
        "sample_code": "def solve(a, b):\n    return a + b"
    }

    # 3. Send POST request to create the problem
    create_url = f"{base_url}/problems"
    response = requests.post(create_url, json=problem_payload, headers=auth_headers)

    # 4. Assertions on response
    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}"
    resp_json = response.json()
    assert resp_json.get("message") == "Problem added successfully", \
        f"Unexpected message: {resp_json.get('message')}"
    created_problem = resp_json.get("problem")
    assert isinstance(created_problem, dict), "Response does not contain 'problem' object"

    # Verify that the returned problem data matches the payload
    for key, value in problem_payload.items():
        assert created_problem.get(key) == value, f"Mismatch in field '{key}'"

    # Cleanup: attempt to delete the created problem to keep test environment clean
    problem_id = created_problem.get("id")
    if problem_id:
        delete_url = f"{base_url}/problems/{problem_id}"
        del_resp = requests.delete(delete_url, headers=auth_headers)
        # Deletion may not be implemented; ignore non‑2xx responses
        if del_resp.status_code not in (200, 204):
            print(f"Warning: cleanup delete request returned {del_resp.status_code}")