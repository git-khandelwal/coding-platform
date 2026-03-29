import os
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """
    Base URL for the API under test.
    Can be overridden by the API_BASE_URL environment variable.
    """
    return os.getenv("API_BASE_URL", "http://localhost:5000")

def test_tc004_get_nonexistent_problem_returns_404(base_url):
    """
    TC004 - Verify GET of non‑existent problem returns 404.
    Steps:
    1. Choose a problem ID that does not exist (e.g., 9999).
    2. Send a GET request to the problem‑details endpoint for that ID.
    Expected:
    - Response status 404 Not Found.
    - Response body indicates the problem does not exist.
    """
    nonexistent_id = 9999
    url = f"{base_url}/problems/{nonexistent_id}"
    response = requests.get(url)

    # Assert that the request completed and returned a 404 status code
    assert response.status_code == 404, f"Expected status code 404, got {response.status_code}"

    # Assert that the response body contains an indication that the problem was not found
    # The implementation returns the plain text "Problem not found"
    assert "Problem not found" in response.text, (
        "Response body does not indicate missing problem. "
        f"Body received: {response.text!r}"
    )