# Developed By John Wick
import os
import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
LOGIN_ENDPOINT = f"{BASE_URL}/login"
PROBLEMS_ENDPOINT = f"{BASE_URL}/problems"
ADD_PROBLEM_ENDPOINT = f"{BASE_URL}/problems/add"

@pytest.fixture(scope="session")
def auth_token():
    """
    Authenticate and return a valid JWT access token.
    """
    credentials = {
        "username": os.getenv("TEST_USERNAME", "testuser"),
        "password": os.getenv("TEST_PASSWORD", "testpass")
    }
    response = requests.post(LOGIN_ENDPOINT, json=credentials)
    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json().get("access_token")
    assert token, "No access_token found in login response"
    return token

@pytest.fixture
def create_problem(auth_token):
    """
    Create a new problem and return its ID.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    problem_data = {
        "title": "Sample Problem",
        "description": "A simple test problem.",
        "difficulty": "Easy",
        "input_format": "Single integer",
        "output_format": "Single integer",
        "sample_input": "[1]",
        "sample_output": "[1]",
        "sample_code": "def solve(): pass",
        "constraints": "None"
    }
    response = requests.post(ADD_PROBLEM_ENDPOINT, json=problem_data, headers=headers)
    assert response.status_code == 200, f"Problem creation failed: {response.text}"
    problem_id = response.json().get("id")
    assert problem_id, "No problem ID returned after creation"
    yield problem_id
    # Teardown: attempt to delete the problem if a delete endpoint exists
    delete_endpoint = f"{PROBLEMS_ENDPOINT}/{problem_id}"
    requests.delete(delete_endpoint, headers=headers)

def test_update_problem_with_valid_token(auth_token, create_problem):
    """
    TC006: Verify that an authenticated PUT request updates a problem’s details
    and returns a success message.
    """
    problem_id = create_problem
    update_endpoint = f"{PROBLEMS_ENDPOINT}/{problem_id}"
    headers = {"Authorization": f"Bearer {auth_token}"}
    update_payload = {"difficulty": "Medium"}

    response = requests.put(update_endpoint, json=update_payload, headers=headers)

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    json_resp = response.json()
    assert "message" in json_resp, "Response JSON does not contain 'message'"
    assert json_resp["message"] == "Problem updated successfully", (
        f"Unexpected message: {json_resp['message']}"
    )
    # Optional: verify that the difficulty was actually updated
    get_response = requests.get(update_endpoint, headers=headers)
    assert get_response.status_code == 200, "Failed to retrieve updated problem"
    problem_data = get_response.json()
    assert problem_data.get("difficulty") == "Medium", "Difficulty not updated correctly"