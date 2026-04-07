import os
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """
    Base URL for the API under test.
    Can be overridden by setting the TEST_BASE_URL environment variable.
    """
    return os.getenv("TEST_BASE_URL", "http://localhost:5000")

def test_tc003_retrieve_problems_list(base_url):
    """
    TC003 - Retrieve list of all problems
    Verify that the GET /problems endpoint returns an HTML page with the problem catalogue.
    """
    endpoint = f"{base_url}/problems"
    response = requests.get(endpoint)

    # Expected Result 1: HTTP 200 OK
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    # Expected Result 2: Response body is an HTML page containing a list of problem titles.
    # Verify Content-Type header indicates HTML.
    content_type = response.headers.get("Content-Type", "")
    assert "text/html" in content_type.lower(), f"Expected 'text/html' in Content-Type, got '{content_type}'"

    # Basic sanity check that the body looks like HTML.
    html_snippet = response.text.strip().lower()
    assert html_snippet.startswith("<!doctype html>") or html_snippet.startswith("<html"), "Response does not appear to be an HTML document"

    # Check for presence of a list element that would typically hold problem titles.
    # This is a generic check; specific titles are not asserted due to lack of concrete data.
    assert ("<ul" in response.text.lower()) or ("<ol" in response.text.lower()), "HTML does not contain an unordered or ordered list, expected problem catalogue"

    # Optional: ensure that the page contains the word 'problem' (case-insensitive) as a minimal indicator.
    assert "problem" in response.text.lower(), "HTML page does not contain the word 'problem'"