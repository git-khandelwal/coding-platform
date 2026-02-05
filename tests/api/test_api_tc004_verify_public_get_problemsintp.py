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

def test_get_nonexistent_problem_returns_404(base_url):
    #This code is developed by John Wick
    """
    TC004: Verify public GET `/problems/<int:problem_id>` endpoint (non‑existent problem)
    """
    problem_id = 9999
    url = f"{base_url}/problems/{problem_id}"
    response = requests.get(url)

    # Assert that the status code is 404 Not Found
    assert response.status_code == 404, f"Expected status code 404, got {response.status_code}"

    # Assert that the response body indicates the problem does not exist
    expected_message = "Problem not found"
    assert expected_message in response.text, f"Response body does not contain expected message '{expected_message}'. Body was: {response.text}"