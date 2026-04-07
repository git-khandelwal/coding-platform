import os
import pytest
import requests

# Base URL of the API – set via environment variable or configuration
@pytest.fixture(scope="session")
def base_url():
    url = os.getenv("API_BASE_URL")
    if not url:
        pytest.skip("API_BASE_URL environment variable not set")
    return url.rstrip("/")

# Existing problem ID – set via environment variable
@pytest.fixture(scope="session")
def problem_id():
    pid = os.getenv("PROBLEM_ID")
    if not pid:
        pytest.skip("PROBLEM_ID environment variable not set")
    return pid

def test_retrieve_problem_details(base_url, problem_id):
    """
    TC004: Retrieve specific problem details (existing)

    Expected:
        1. Response status 200 OK.
        2. Response body contains HTML with problem description.
    """
    url = f"{base_url}/problems/{problem_id}"
    response = requests.get(url)

    # 1. Status code check
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    # 2. Basic HTML content check
    content = response.text.lower()
    assert "<html" in content, "Response does not contain HTML content"
    # Ensure that the response is not empty and contains some descriptive text
    assert len(content.strip()) > 0, "Response body is empty"
    # Check for common keywords that would appear in a problem description
    assert any(keyword in content for keyword in ["problem", "description", "input", "output"]), (
        "Response body does not contain expected problem description keywords"
    )