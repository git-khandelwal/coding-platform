import os
import pytest
import requests


@pytest.fixture(scope="session")
def api_base_url():
    """
    Base URL of the API under test.
    Can be overridden by setting the environment variable API_BASE_URL.
    """
    return os.getenv("API_BASE_URL", "http://localhost:5000")


@pytest.fixture(scope="session")
def problem_id():
    """
    Problem ID to be used for the submissions‑history endpoint.
    Must correspond to an existing problem in the test environment.
    Can be overridden by setting the environment variable PROBLEM_ID.
    """
    return int(os.getenv("PROBLEM_ID", "1"))


def test_tc011_retrieve_submission_history_without_authentication(api_base_url, problem_id):
    """
    TC011 – Verify that the submissions‑history endpoint rejects unauthenticated access.
    Steps:
        1. Send a GET request to /problems/<problem_id>/submissions without an Authorization header.
        2. Assert that the response status is 401 Unauthorized and that the body indicates a missing or invalid token.
    """
    url = f"{api_base_url}/problems/{problem_id}/submissions"

    response = requests.get(url)

    # Expected status code
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"

    # Expected error indication – the exact format may vary, so we perform a flexible check
    try:
        json_body = response.json()
        # Common keys used by Flask-JWT-Extended for auth errors
        error_msg = json_body.get("msg") or json_body.get("message") or ""
    except ValueError:
        # If response is not JSON, fall back to raw text
        error_msg = response.text

    assert error_msg, "Response should contain an error message indicating missing or invalid token"
    assert "token" in error_msg.lower(), f"Error message does not mention token: {error_msg}"