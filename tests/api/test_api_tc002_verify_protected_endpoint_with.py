import os
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """
    Base URL of the API under test.

    The environment variable `API_BASE_URL` can be set to override the default.
    Example: http://localhost:5000
    """
    return os.getenv("API_BASE_URL", "http://localhost:5000")


def test_protected_endpoint_without_jwt(base_url):
    """
    TC002 - Verify protected endpoint without JWT.

    Steps:
    1. Send a GET request to the /protected endpoint without an Authorization header.
    2. Assert that the response status is 401 Unauthorized.
    3. Assert that the response body contains an error message indicating a missing or invalid token.
    """
    url = f"{base_url}/protected"
    response = requests.get(url)

    # Expected status code
    assert response.status_code == 401, f"Expected status code 401, got {response.status_code}"

    # Expected error message (Flask-JWT-Extended returns a JSON with a 'msg' field)
    try:
        json_body = response.json()
    except ValueError:
        pytest.fail("Response is not valid JSON")

    assert "msg" in json_body, "Response JSON should contain a 'msg' field indicating the error"
    assert json_body["msg"], "Error message should not be empty"
    # Common messages include "Missing Authorization Header" or "Invalid JWT"
    # We check that the message mentions token issues
    token_error_indicators = ["Missing", "Invalid", "token"]
    assert any(indicator.lower() in json_body["msg"].lower() for indicator in token_error_indicators), (
        f"Error message does not indicate missing or invalid token: {json_body['msg']}"
    )