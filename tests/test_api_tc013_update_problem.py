import pytest
import requests

# Gaps in context:
# - Base URL for the API is not provided.
# - Endpoints for user registration and login are not provided.
# - Exact structure of the login and problem objects is not fully defined.
# - Test user credentials and problem data are not specified.
# - There is no teardown endpoint for deleting test users or problems.

# Please set the following according to your environment:
BASE_URL = "http://localhost:5000"
REGISTER_URL = f"{BASE_URL}/register"
LOGIN_URL = f"{BASE_URL}/login"
ADD_PROBLEM_URL = f"{BASE_URL}/problems/add"
UPDATE_PROBLEM_URL_TEMPLATE = f"{BASE_URL}/problems/{{problem_id}}"

TEST_USERNAME = "testuser_tc013"
TEST_PASSWORD = "TestPass123!"

@pytest.fixture(scope="module")
def auth_token():
    # Register user (ignore errors if already exists)
    requests.post(REGISTER_URL, json={
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    })

    # Login to get JWT token
    login_resp = requests.post(LOGIN_URL, json={
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    })
    assert login_resp.status_code == 200, "Login failed, cannot obtain JWT token"
    token = login_resp.json().get("access_token")
    assert token, "No access_token found in login response"
    return token

@pytest.fixture
def created_problem(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    problem_data = {
        "title": "Original Title TC013",
        "description": "Original Description",
        "difficulty": "Easy",
        "input_format": "int n",
        "output_format": "int result",
        "sample_input": "1",
        "sample_output": "2",
        "sample_code": "print(2)",
        "constraints": "1 <= n <= 100"
    }
    resp = requests.post(ADD_PROBLEM_URL, json=problem_data, headers=headers)
    assert resp.status_code == 201, f"Problem creation failed: {resp.text}"
    # The API returns the problem object in the response, but no ID is specified in the sample.
    # We need the ID for updating.
    # If the response includes the created problem with an ID, extract it:
    problem_id = None
    if "problem" in resp.json():
        problem = resp.json()["problem"]
        problem_id = problem.get("id")
    # If not, try to get it from the Location header or another way
    if not problem_id:
        # Try to get the list of problems and find the one with the unique title
        list_resp = requests.get(f"{BASE_URL}/problems")
        # The /problems endpoint returns HTML, so we cannot parse it reliably without more context.
        # There is a gap here: no reliable way to get the problem ID.
        pytest.skip("Cannot determine created problem ID from API response; test cannot proceed without this information.")
    yield problem_id
    # Teardown: No endpoint provided to delete a problem, so cannot clean up.

def test_tc013_update_problem(auth_token, created_problem):
    """
    TC013: Verify that an authenticated user can update an existing problem.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    update_data = {
        "title": "Updated Title TC013",
        "description": "Updated Description",
        "difficulty": "Medium",
        "input_format": "int n, int m",
        "output_format": "int result",
        "sample_input": "2 3",
        "sample_output": "5",
        "sample_code": "print(5)",
        "constraints": "1 <= n, m <= 100"
    }
    update_url = UPDATE_PROBLEM_URL_TEMPLATE.format(problem_id=created_problem)
    resp = requests.put(update_url, json=update_data, headers=headers)
    assert resp.status_code == 200, f"Expected 200 OK, got {resp.status_code}: {resp.text}"
    resp_json = resp.json()
    assert "message" in resp_json, "No 'message' in response"
    assert resp_json["message"] == "Problem updated successfully", f"Unexpected message: {resp_json['message']}"