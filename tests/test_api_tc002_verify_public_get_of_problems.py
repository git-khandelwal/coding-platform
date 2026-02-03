import os
import re

import pytest
import requests


@pytest.fixture(scope="session")
def base_url():
    """
    Base URL for the API under test.
    Can be overridden by setting the API_URL environment variable.
    """
    return os.getenv("API_URL", "http://localhost:5000")


def is_html(content: str) -> bool:
    """Simple check to see if the response looks like HTML."""
    return bool(re.search(r"<\s*html", content, re.IGNORECASE))


def contains_problem_titles(content: str) -> bool:
    """
    Heuristic to verify that the HTML contains at least one problem title.
    Looks for typical HTML list structures or heading tags with non‑empty text.
    """
    # Look for <li> or <h2>/<h3> elements with some text
    patterns = [
        r"<\s*li[^>]*>[^<]+</\s*li>",
        r"<\s*h[2-3][^>]*>[^<]+</\s*h[2-3]>"
    ]
    return any(re.search(p, content, re.IGNORECASE) for p in patterns)


def test_public_get_problems_list_returns_html(base_url):
    """
    TC002 - Verify public GET of problems list.
    Sends a GET request to the problems list endpoint without authentication
    and asserts that the response is successful, has a 200 status code,
    and contains HTML with a list of problem titles.
    """
    endpoint = f"{base_url}/problems"
    response = requests.get(endpoint, timeout=10)

    # 1. Request succeeds and returns HTTP 200
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    # 2. Response Content-Type indicates HTML
    content_type = response.headers.get("Content-Type", "")
    assert "text/html" in content_type.lower(), f"Expected 'text/html' in Content-Type, got '{content_type}'"

    # 3. Response body is HTML and contains problem titles
    body = response.text
    assert is_html(body), "Response body does not appear to be HTML"
    assert contains_problem_titles(body), "HTML does not contain any recognizable problem titles or list items"