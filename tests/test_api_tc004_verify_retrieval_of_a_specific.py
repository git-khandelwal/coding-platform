import os
import re

import pytest
import requests


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the API under test."""
    return os.getenv("API_BASE_URL", "http://localhost:5000")


@pytest.fixture
def problem_id():
    """Known existing problem ID for the test."""
    return 1


def test_tc004_get_existing_problem(base_url, problem_id):
    """
    TC004 – Verify retrieval of a specific problem (existing).

    Steps:
    1. Send GET request to /problems/<problem_id>.
    2. Assert HTTP 200.
    3. Assert Content‑Type is text/html.
    4. Assert response body contains problem title, description and difficulty.
    """
    url = f"{base_url}/problems/{problem_id}"
    response = requests.get(url)

    # 1. HTTP 200
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

    # 2. Content‑Type header
    content_type = response.headers.get("Content-Type", "")
    assert "text/html" in content_type, f"Expected 'text/html' in Content-Type, got '{content_type}'"

    # 3. Basic content checks
    html = response.text

    # Look for typical markers – these are generic and should exist in a problem detail page.
    # Adjust the patterns if the actual HTML uses different identifiers.
    title_pattern = re.compile(r"<h1[^>]*>.*?</h1>", re.IGNORECASE | re.DOTALL)
    description_pattern = re.compile(r"<div[^>]*class=[\"']?description[\"']?[^>]*>.*?</div>", re.IGNORECASE | re.DOTALL)
    difficulty_pattern = re.compile(r"<span[^>]*class=[\"']?difficulty[\"']?[^>]*>.*?</span>", re.IGNORECASE | re.DOTALL)

    assert title_pattern.search(html), "Problem title not found in response HTML"
    assert description_pattern.search(html), "Problem description not found in response HTML"
    assert difficulty_pattern.search(html), "Problem difficulty not found in response HTML"