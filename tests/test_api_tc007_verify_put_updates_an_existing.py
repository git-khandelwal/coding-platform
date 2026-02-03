import os
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """Base URL for the API under test."""
    return os.getenv("API_BASE_URL", "http://localhost:5000")

@pytest.fixture(scope="session")
def credentials():
    """Credentials for an existing test user."""
    return {
        "username": os.getenv("TEST_USERNAME", "testuser"),
        "password": os.getenv("TEST_PASSWORD", "testpass")
    }

@pytest.fixture(scope="session")
def auth_token(base_url, credentials):
    """Obtain a JWT token using the login endpoint."""
    login_url = f"{base_url}/auth/login"
    resp = requests.post(login_url, json=credentials)
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    data = resp.json()
    token = data.get("access_token") or data.get("token")
    assert token, "JWT token not found in login response"
    return token

@pytest.fixture
def created_problem(base_url, auth_token):
    """
    Create a temporary problem to be used in the PUT test.
    Yields the problem dict and ensures cleanup after the test.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    create_url = f"{base_url}/problems/add"
    payload = {
        "title": "Temp Problem",
        "description": "Temporary problem for API testing",
        "difficulty": "Easy",
        "input_format": "N/A",
        "output_format": "N/A",
        "sample_input": "1",
        "sample_output": "1",
        "sample_code": "",
        "constraints": ""
    }
    resp = requests.post(create_url, json=payload, headers=headers)
    assert resp.status_code == 200, f"Problem creation failed: {resp.text}"
    problem = resp.json()
    problem_id = problem.get("id")
    assert problem_id, "Created problem ID not returned"

    # Provide the problem data to the test
    yield {"id": problem_id, "original": payload}

    # Teardown: attempt to revert the problem to its original state
    revert_url = f"{base_url}/problems/{problem_id}"
    requests.put(revert_url, json=payload, headers=headers)


def test_put_updates_existing_problem(base_url, auth_token, created_problem):
    """
    TC007: Verify PUT updates an existing problem.
    Steps:
    1. Obtain JWT (handled by fixture).
    2. Use an existing problem ID (created by fixture).
    3. Send PUT with updated fields.
    4. Verify response status and message.
    5. GET the problem and confirm the field was updated.
    """
    problem_id = created_problem["id"]
    original_data = created_problem["original"]
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Step 3: Update the problem's difficulty to "Hard"
    update_payload = {"difficulty": "Hard"}
    put_url = f"{base_url}/problems/{problem_id}"
    put_resp = requests.put(put_url, json=update_payload, headers=headers)

    # Expected Result 1 & 2: Request succeeds with 200 OK
    assert put_resp.status_code == 200, f"PUT request failed: {put_resp.text}"

    # Expected Result 3: Response body contains confirmation message
    put_json = put_resp.json()
    assert "message" in put_json, "Response missing 'message' field"
    assert "Problem updated successfully" in put_json["message"], "Unexpected update message"

    # Step 4: GET the problem to verify the update
    get_url = f"{base_url}/problems/{problem_id}"
    get_resp = requests.get(get_url, headers=headers)
    assert get_resp.status_code == 200, f"GET after update failed: {get_resp.text}"

    # Assuming the GET endpoint returns JSON with problem details
    problem_data = get_resp.json()
    assert problem_data.get("difficulty") == "Hard", "Difficulty field was not updated"
    # Ensure other fields remain unchanged
    for field in ["title", "description", "input_format", "output_format", "sample_input", "sample_output", "sample_code", "constraints"]:
        assert problem_data.get(field) == original_data.get(field), f"Field '{field}' was unexpectedly modified"