# Developed By John Wick
import os
import pytest
import requests

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")

@pytest.fixture(scope="module")
def api_base_url():
    return BASE_URL

def test_retrieve_nonexistent_problem(api_base_url):
    """
    Test Case ID: TC003
    Summary: Retrieve non‑existent problem (GET)
    """
    invalid_problem_id = 9999
    url = f"{api_base_url}/problems/{invalid_problem_id}"
    response = requests.get(url)

    # Assert that the status code is 404
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    # Assert that the response body contains an error message indicating the problem does not exist
    assert "Problem not found" in response.text, (
        f"Expected error message 'Problem not found' in response, got: {response.text}"
    )