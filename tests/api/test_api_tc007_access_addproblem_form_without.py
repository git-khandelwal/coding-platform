import os
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """
    Base URL for the API under test.
    Can be overridden by setting the API_BASE_URL environment variable.
    """
    return os.getenv("API_BASE_URL", "http://localhost:5000")

def test_add_problem_form_unauthenticated(base_url):
    """
    TC007 - Access add‑problem form without authentication.
    Sends a GET request to the /problems/add endpoint without any JWT
    and verifies that the response is 401 Unauthorized with an appropriate
    error message.
    """
    endpoint = f"{base_url}/problems/add"
    response = requests.get(endpoint)

    # Assert HTTP status code
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"

    # Attempt to parse JSON error payload; Flask-JWT-Extended typically returns {"msg": "..."}
    try:
        payload = response.json()
    except ValueError:
        pytest.fail("Response is not valid JSON")

    # Verify that an error message indicating missing/invalid token is present
    assert "msg" in payload, "Expected 'msg' key in error response payload"
    error_msg = payload["msg"].lower()
    assert "missing" in error_msg or "invalid" in error_msg, (
        f"Error message does not indicate missing or invalid token: '{payload['msg']}'"
    )