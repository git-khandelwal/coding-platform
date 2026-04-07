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
    TC007 - Verify denial of add‑problem form without authentication.
    Sends a GET request to /problems/add without an Authorization header
    and asserts that the response is HTTP 401 with an appropriate error message.
    """
    endpoint = f"{base_url}/problems/add"
    response = requests.get(endpoint)

    # Expected HTTP status code
    assert response.status_code == 401, f"Expected status code 401, got {response.status_code}"

    # Expected error indication in response body (token related)
    response_text = response.text.lower()
    assert (
        "token" in response_text or "missing" in response_text or "invalid" in response_text
    ), "Response does not indicate missing or invalid token"