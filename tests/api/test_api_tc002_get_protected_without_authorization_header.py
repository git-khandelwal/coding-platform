import json
import pytest
import requests

# NOTE: The base URL of the API under test is not specified in the provided context.
# Replace 'http://localhost:5000' with the actual address where the Flask application is running.
BASE_URL = "http://localhost:5000"


@pytest.fixture(scope="module")
def api_base_url():
    """Provide the base URL for the API."""
    return BASE_URL


def test_get_protected_without_authorization(api_base_url):
    """
    TC002: Verify that omitting the Authorization header results in an unauthorized error.
    """
    url = f"{api_base_url}/protected"
    response = requests.get(url)

    # Expected: 401 Unauthorized
    assert response.status_code == 401, f"Expected status 401, got {response.status_code}"

    # Expected: JSON body contains an error message indicating missing or invalid token
    try:
        data = response.json()
    except json.JSONDecodeError:
        pytest.fail("Response is not valid JSON")

    assert isinstance(data, dict), "Response JSON is not a dictionary"
    assert "error" in data, "Response JSON does not contain 'error' key"
    # Optional: check that the error message mentions token
    error_msg = data.get("error", "").lower()
    assert "token" in error_msg or "auth" in error_msg, (
        f"Error message does not mention token or auth: {error_msg}"
    )