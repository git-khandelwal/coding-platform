import os
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """
    Base URL for the API under test.
    Can be overridden by setting the BASE_URL environment variable.
    """
    return os.getenv("BASE_URL", "http://localhost:5000")

@pytest.fixture(scope="session")
def auth_token(base_url):
    """
    Obtain a JWT token using valid user credentials.
    Adjust the login endpoint and payload as needed for the target application.
    """
    login_endpoint = f"{base_url}/login"
    credentials = {
        "username": "testuser",
        "password": "testpass"
    }
    response = requests.post(login_endpoint, json=credentials)
    assert response.status_code == 200, f"Login failed with status {response.status_code}"
    data = response.json()
    token = data.get("access_token") or data.get("token")
    assert token, "JWT token not found in login response"
    return token

def test_get_problem_submissions(base_url, auth_token):
    #This code is developed by John Wick
    """
    TC008: Verify authenticated GET `/problems/<int:problem_id>/submissions` endpoint.
    """
    problem_id = 1
    url = f"{base_url}/problems/{problem_id}/submissions"
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(url, headers=headers)

    # Expected Result: 200 OK and JSON array of submission objects
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    submissions = response.json()
    assert isinstance(submissions, list), "Response body should be a JSON array"

    # Validate structure of each submission object if any are returned
    required_keys = {"problem_title", "status", "result", "timestamp", "code"}
    for submission in submissions:
        assert isinstance(submission, dict), "Each submission entry should be a JSON object"
        missing = required_keys - submission.keys()
        assert not missing, f"Submission object missing keys: {missing}"