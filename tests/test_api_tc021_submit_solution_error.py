import pytest
import requests

# Gaps in information:
# - No base URL provided for the API.
# - No test user credentials or registration endpoint details.
# - No specific problem_id to use for submission.
# - No details about the structure of the login endpoint or payload.
# - No details about the code language or error format expected.

@pytest.fixture(scope="module")
def base_url():
    # GAP: Replace with actual base URL of the API, e.g., "http://localhost:5000"
    return "http://localhost:5000"

@pytest.fixture(scope="module")
def test_user_credentials():
    # GAP: Replace with actual test user credentials
    return {
        "username": "testuser_tc021",
        "password": "TestPassword123!"
    }

@pytest.fixture(scope="module")
def jwt_token(base_url, test_user_credentials):
    # GAP: Replace '/login' and payload as per actual API
    login_url = f"{base_url}/login"
    response = requests.post(login_url, json=test_user_credentials)
    assert response.status_code == 200, "Login failed, cannot obtain JWT token"
    data = response.json()
    # GAP: Replace 'access_token' with the actual token key if different
    assert "access_token" in data, "No access_token in login response"
    return data["access_token"]

@pytest.fixture(scope="module")
def problem_id(base_url, jwt_token):
    # GAP: Replace with actual logic to get or create a problem and return its ID
    # For now, attempt to get the first problem in the list
    problems_url = f"{base_url}/problems"
    # The /problems endpoint appears to return HTML, not JSON, based on code context
    # GAP: No API endpoint for listing problems as JSON is provided
    # Test cannot proceed without a valid problem_id
    pytest.skip("No API endpoint for retrieving problem_id as JSON. Cannot proceed with test.")

@pytest.fixture(scope="function")
def error_code():
    # Python code with a syntax error
    return "def solution()\n    return 42"

def test_tc021_submit_solution_error(base_url, jwt_token, problem_id, error_code):
    # GAP: Endpoint expects POST to /problems/<int:problem_id>/solve with JSON body {"code": ...}
    url = f"{base_url}/problems/{problem_id}/solve"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "code": error_code
    }
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    data = response.json()
    assert "status" in data, "Response JSON missing 'status' field"
    assert data["status"] == "Error", f"Expected status 'Error', got '{data['status']}'"