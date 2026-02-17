import os
import pytest
import requests

BASE_URL = os.getenv("API_BASE_URL")
USERNAME = os.getenv("API_USERNAME")
PASSWORD = os.getenv("API_PASSWORD")
PROBLEM_ID = os.getenv("API_PROBLEM_ID")


@pytest.fixture(scope="session")
def auth_token():
    """
    Obtain a JWT for an authenticated user.

    Expected environment variables:
        - API_BASE_URL: Base URL of the API (e.g., http://localhost:5000)
        - API_USERNAME: Username for login
        - API_PASSWORD: Password for login

    The login endpoint and response format are not defined in the provided
    context. Adjust the ``login_url`` and token extraction logic as needed.
    """
    if not all([BASE_URL, USERNAME, PASSWORD]):
        pytest.skip("Authentication details not provided via environment variables")
    # NOTE: The exact login endpoint is unknown; replace '/login' if different.
    login_url = f"{BASE_URL}/login"
    response = requests.post(login_url, json={"username": USERNAME, "password": PASSWORD})
    assert response.status_code == 200, f"Login request failed with status {response.status_code}"
    json_resp = response.json()
    token = json_resp.get("access_token") or json_resp.get("token")
    if not token:
        pytest.fail("JWT token not found in login response")
    return token


@pytest.fixture
def problem_id():
    """
    Provide a valid problem ID for the test.

    Expected environment variable:
        - API_PROBLEM_ID: ID of an existing problem with at least one submission.
    """
    if not PROBLEM_ID:
        pytest.skip("Problem ID not provided via environment variable API_PROBLEM_ID")
    return PROBLEM_ID


def test_tc010_retrieve_submission_history(auth_token, problem_id):
    """
    TC010 – Retrieve submission history for a problem.

    Steps:
    1. Use the JWT obtained from ``auth_token`` fixture.
    2. Use the ``problem_id`` fixture.
    3. Send a GET request to the submissions‑history endpoint.
    4. Verify response status and payload.
    """
    if not BASE_URL:
        pytest.skip("API_BASE_URL not set; cannot construct request URL")
    # Endpoint path derived from code context: /problems/<int:problem_id>/submissions
    url = f"{BASE_URL}/problems/{problem_id}/submissions"
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(url, headers=headers)

    # Expected Result: 200 OK
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    # Expected Result: JSON array of submission objects with required fields
    try:
        submissions = response.json()
    except ValueError:
        pytest.fail("Response is not valid JSON")

    assert isinstance(submissions, list), "Response JSON is not a list"

    required_fields = {"problem_title", "status", "result", "timestamp", "code"}
    for idx, submission in enumerate(submissions):
        assert isinstance(submission, dict), f"Submission at index {idx} is not a JSON object"
        missing = required_fields - submission.keys()
        assert not missing, f"Submission at index {idx} missing fields: {missing}"