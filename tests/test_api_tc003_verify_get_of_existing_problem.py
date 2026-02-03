import os
import re
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """
    Base URL for the API under test.
    Can be overridden by setting the API_BASE_URL environment variable.
    """
    return os.getenv("API_BASE_URL", "http://localhost:5000")

@pytest.fixture(scope="session")
def existing_problem_id():
    """
    Returns a known existing problem ID.
    Adjust this value if the test environment uses a different seed.
    """
    return 1

def test_tc003_get_existing_problem_details(base_url, existing_problem_id):
    """
    TC003 – Verify GET of existing problem details.
    Steps:
    1. Send a GET request to the problem‑details endpoint for a known problem ID.
    Expected:
    - HTTP 200 OK
    - Response body is HTML containing the problem title, description, and difficulty.
    """
    url = f"{base_url}/problems/{existing_problem_id}"
    response = requests.get(url)

    # Assert request succeeded with status 200
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

    # Basic check that the response is HTML
    content_type = response.headers.get("Content-Type", "")
    assert "text/html" in content_type.lower(), f"Expected HTML content type, got '{content_type}'"

    html = response.text

    # Verify that key problem fields appear in the HTML.
    # These checks are deliberately simple to avoid coupling to exact markup.
    required_fields = ["title", "description", "difficulty"]
    for field in required_fields:
        pattern = re.compile(rf">{field}[:\s]*</?[^>]*>", re.IGNORECASE)
        assert re.search(pattern, html) or field.lower() in html.lower(), (
            f"Expected '{field}' to appear in the problem details HTML."
        )