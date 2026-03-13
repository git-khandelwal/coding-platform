import os
import re
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """Base URL for the API under test."""
    return os.getenv("API_URL", "http://localhost:5000")

def test_tc012_submission_history_without_authentication(base_url):
    """
    TC012 – Verify denial of submission history without authentication.
    Sends a GET request to /problems/1/submissions without an Authorization header
    and asserts that the response is HTTP 401 with an appropriate error message.
    """
    endpoint = f"{base_url}/problems/1/submissions"
    response = requests.get(endpoint)

    # Assert HTTP 401 Unauthorized
    assert response.status_code == 401, f"Expected status code 401, got {response.status_code}"

    # The response should indicate a missing or invalid token.
    # Accept either JSON with an error field or plain text containing the word "token".
    content_type = response.headers.get("Content-Type", "")
    if "application/json" in content_type:
        try:
            json_body = response.json()
        except ValueError:
            pytest.fail("Response claimed to be JSON but could not be parsed.")
        # Look for typical error keys
        error_message = (
            json_body.get("msg")
            or json_body.get("error")
            or json_body.get("message")
            or ""
        )
        assert error_message, "JSON response does not contain an error message."
        assert re.search(r"token", error_message, re.IGNORECASE), (
            f"Error message does not mention token: '{error_message}'"
        )
    else:
        # Fallback to plain text check
        text = response.text
        assert text, "Response body is empty."
        assert re.search(r"token", text, re.IGNORECASE), (
            f"Response does not mention token: '{text}'"
        )