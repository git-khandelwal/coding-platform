import os
import re
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """
    Base URL for the API under test.
    Can be overridden by setting the PROBLEMS_API_URL environment variable.
    """
    return os.getenv("PROBLEMS_API_URL", "http://localhost:5000")

def test_tc003_retrieve_problem_list(base_url):
    """
    TC003: Verify retrieval of problem list.
    Steps:
    1. Send GET request to /problems.
    2. Assert HTTP 200 and Content-Type text/html.
    3. Assert response contains at least one problem title element.
    """
    url = f"{base_url.rstrip('/')}/problems"
    response = requests.get(url)

    # Assert status code
    assert response.status_code == 200, f"Expected HTTP 200, got {response.status_code}"

    # Assert Content-Type header
    content_type = response.headers.get("Content-Type", "")
    assert "text/html" in content_type.lower(), f"Expected Content-Type to include 'text/html', got '{content_type}'"

    # Assert presence of at least one problem title in HTML
    html = response.text
    pattern = re.compile(r'<div\s+class=["\']problem-title["\']', re.IGNORECASE)
    matches = pattern.findall(html)
    assert matches, "Expected at least one '<div class=\"problem-title\">' element in the response HTML"