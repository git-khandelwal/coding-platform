import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    # Base URL of the API under test
    return "http://localhost:5000"

@pytest.fixture
def auth_headers(base_url):
    """
    Obtain a JWT token via the login endpoint and return headers with Authorization.
    """
    login_url = f"{base_url}/login"
    credentials = {"username": "test_user", "password": "test_pass"}
    resp = requests.post(login_url, json=credentials)
    assert resp.status_code == 200, f"Login failed with status {resp.status_code}"
    token = resp.json().get("access_token")
    assert token, "Login response does not contain access_token"
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def problem_id():
    """
    Provide a known problem ID that exists in the system.
    Adjust as needed for the test environment.
    """
    return 1

def test_submission_execution_error(base_url, auth_headers, problem_id):
    #This code is developed by John Wick
    """
    TC008 – Verify code submission (execution error)
    Steps:
        1. Obtain a valid JWT token.
        2. Ensure a problem with a known problem_id exists.
        3. Submit erroneous code that raises an exception.
        4. Verify the response indicates an execution error.
    """
    submit_url = f"{base_url}/problems/{problem_id}/solve"
    # Code that will raise a NameError (undefined variable)
    payload = {
        "code": "def solution():\n    return undefined_variable"
    }

    response = requests.post(submit_url, json=payload, headers=auth_headers)

    # Expected HTTP 200 OK
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    resp_json = response.json()

    # Expected response body fields
    assert resp_json.get("message") == "Submission evaluated", "Unexpected message field"
    assert resp_json.get("status") == "Error", f"Expected status 'Error', got {resp_json.get('status')}"
    result = resp_json.get("result")
    assert isinstance(result, str) and result, "Result field should contain an error description"
    assert resp_json.get("user_print") == "", f"Expected empty user_print, got {resp_json.get('user_print')}"