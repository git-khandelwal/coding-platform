import re
import pytest
import requests


@pytest.fixture(scope="session")
def base_url():
    # Adjust the base URL as needed for the test environment
    return "http://localhost:5000"


def test_put_problem_without_authentication(base_url):
    """
    TC010: Verify problem update via PUT without authentication.
    Sends a PUT request to /problems/1 without an Authorization header
    and expects a 401 Unauthorized response indicating a missing or invalid token.
    """
    problem_id = 1
    url = f"{base_url}/problems/{problem_id}"
    payload = {"title": "Updated Title"}  # valid JSON payload

    response = requests.put(url, json=payload)  # No Authorization header

    # Assert HTTP status code
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"

    # Determine response body content for token error verification
    if response.headers.get("Content-Type", "").startswith("application/json"):
        try:
            body_content = response.json()
        except ValueError:
            body_content = response.text
    else:
        body_content = response.text

    # Convert body content to string for regex search
    body_str = str(body_content)

    # Assert that the response indicates a missing or invalid token
    assert re.search(r"missing|invalid|token", body_str, re.IGNORECASE), (
        "Response does not contain indication of missing or invalid token."
    )