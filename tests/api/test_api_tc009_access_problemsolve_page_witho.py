import os
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """
    Base URL of the API under test.
    Must be provided via the `API_BASE_URL` environment variable.
    """
    url = os.getenv("API_BASE_URL")
    if not url:
        raise RuntimeError(
            "Environment variable 'API_BASE_URL' is not set. "
            "Provide the base URL of the API (e.g., http://localhost:5000)."
        )
    return url.rstrip("/")

@pytest.fixture(scope="session")
def problem_id():
    """
    Identifier of an existing problem to be used for the solve‑page endpoint.
    Must be provided via the `TEST_PROBLEM_ID` environment variable.
    """
    pid = os.getenv("TEST_PROBLEM_ID")
    if not pid:
        raise RuntimeError(
            "Environment variable 'TEST_PROBLEM_ID' is not set. "
            "Provide a valid problem ID that exists in the test environment."
        )
    try:
        return int(pid)
    except ValueError:
        raise RuntimeError(
            f"Invalid problem ID '{pid}'. It must be an integer."
        )

def test_tc009_access_solve_page_without_authentication(base_url, problem_id):
    """
    TC009 – Verify that the solve‑page endpoint rejects unauthenticated requests.

    Steps:
    1. Send a GET request to /problems/<problem_id>/solve without an Authorization header.
    2. Assert that the response status is 401 Unauthorized and that the body indicates a missing/invalid token.
    """
    endpoint = f"{base_url}/problems/{problem_id}/solve"
    response = requests.get(endpoint)

    # Expected status code
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"

    # Attempt to provide a helpful assertion on the error message.
    # The exact format may vary (JSON, plain text, HTML). We check for common indicators.
    content_type = response.headers.get("Content-Type", "")
    if "application/json" in content_type:
        try:
            body = response.json()
        except ValueError:
            pytest.fail("Response declared JSON but could not be parsed.")
        # Look for typical keys that convey token errors.
        token_error_keys = ["msg", "message", "error", "detail"]
        assert any(
            key in body and isinstance(body[key], str) and "token" in body[key].lower()
            for key in token_error_keys
        ), f"JSON response does not contain a token‑related error message: {body}"
    else:
        # Fallback to plain‑text/HTML search.
        text = response.text.lower()
        assert "token" in text, "Response body does not contain any indication of a missing or invalid token."