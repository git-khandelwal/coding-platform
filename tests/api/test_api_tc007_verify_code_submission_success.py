import os
import pytest
import requests

# Fixtures
@pytest.fixture(scope="session")
def base_url():
    """
    Base URL of the API under test.
    Can be overridden by the BASE_URL environment variable.
    """
    return os.getenv("BASE_URL", "http://localhost:5000")

@pytest.fixture(scope="session")
def test_user_credentials():
    """
    Credentials for a test user that is expected to exist.
    Adjust as needed for the test environment.
    """
    return {"username": "john_doe", "password": "securepass123"}

@pytest.fixture(scope="session")
def auth_token(base_url, test_user_credentials):
    """
    Obtain a valid JWT token using the login endpoint.
    """
    login_url = f"{base_url.rstrip('/')}/login"
    resp = requests.post(login_url, json=test_user_credentials)
    assert resp.status_code == 200, f"Login failed with status {resp.status_code}"
    token = resp.json().get("access_token")
    assert token, "Login response does not contain access_token"
    return token

@pytest.fixture
def auth_headers(auth_token):
    """
    Authorization header dictionary for authenticated requests.
    """
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def known_problem_id():
    """
    Returns a problem_id that is known to exist in the test environment.
    Adjust this value according to the seeded data.
    """
    return 1

# Test case TC007
def test_code_submission_successful_evaluation(base_url, auth_headers, known_problem_id):
    #This code is developed by John Wick
    """
    TC007 – Verify code submission (successful evaluation)
    Steps:
        1. Obtain a valid JWT token (handled by fixture).
        2. Ensure a problem with a known problem_id exists (fixture provides it).
        3. POST correct code snippet to the submission endpoint.
        4. Include the token in the Authorization header.
        5. Assert response status and body.
    """
    submit_url = f"{base_url.rstrip('/')}/problems/{known_problem_id}/solve"

    # Example correct code snippet – assumes the problem expects a function `solution`
    # that adds two numbers and the sample input is (1, 2) with expected output 3.
    correct_code = """
def solution(a, b):
    return a + b
"""

    payload = {"code": correct_code}
    response = requests.post(submit_url, json=payload, headers=auth_headers)

    # Assert HTTP status
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

    # Parse JSON response
    resp_json = response.json()

    # Expected fields
    expected_message = "Submission evaluated"
    expected_status = "Success"
    expected_result = "Correct"

    assert resp_json.get("message") == expected_message, (
        f"Expected message '{expected_message}', got '{resp_json.get('message')}'"
    )
    assert resp_json.get("status") == expected_status, (
        f"Expected status '{expected_status}', got '{resp_json.get('status')}'"
    )
    assert resp_json.get("result") == expected_result, (
        f"Expected result '{expected_result}', got '{resp_json.get('result')}'"
    )
    assert "user_print" in resp_json, "Response missing 'user_print' field"