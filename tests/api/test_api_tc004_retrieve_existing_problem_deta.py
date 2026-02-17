import os
import re
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """
    Base URL for the API under test.
    Adjust the default as needed or set the environment variable API_BASE_URL.
    """
    return os.getenv("API_BASE_URL", "http://localhost:5000")

@pytest.fixture(scope="session")
def valid_problem_id():
    """
    A known existing problem ID.
    The test plan suggests using ID 1, but this fixture can be overridden
    via the environment variable VALID_PROBLEM_ID if the test environment uses a different ID.
    """
    return int(os.getenv("VALID_PROBLEM_ID", "1"))

def test_tc004_retrieve_existing_problem_details(base_url, valid_problem_id):
    """
    TC004 – Retrieve existing problem details

    Steps:
    1. Send a GET request to the problem‑detail endpoint with a valid problem ID.
    2. Verify the response status and content.
    """
    url = f"{base_url}/problems/{valid_problem_id}"
    response = requests.get(url)

    # Expected Result 1: HTTP 200 OK
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    # Expected Result 2: HTML page includes problem title, description, difficulty, and sample data.
    # Since the exact HTML structure is unknown, we perform simple substring checks.
    html = response.text

    # Define regex patterns for the required fields (case‑insensitive)
    patterns = {
        "title": re.compile(r"<title>.*?</title>", re.IGNORECASE),
        "description": re.compile(r"description", re.IGNORECASE),
        "difficulty": re.compile(r"difficulty", re.IGNORECASE),
        "sample_input": re.compile(r"sample\s*input", re.IGNORECASE),
        "sample_output": re.compile(r"sample\s*output", re.IGNORECASE),
    }

    missing = [name for name, pat in patterns.items() if not pat.search(html)]
    assert not missing, f"The response HTML is missing expected sections: {', '.join(missing)}"

    # Optional: Log the URL and a snippet of the response for debugging
    print(f"GET {url} returned 200 OK. Response snippet:\n{html[:200]}...")