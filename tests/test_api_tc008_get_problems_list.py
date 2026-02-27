import pytest
import requests

# NOTE: The base URL and the exact endpoint for the problems list are not specified in the provided context.
# Please set the correct base URL for your environment.
BASE_URL = "http://localhost:5000"
PROBLEMS_LIST_ENDPOINT = "/problems"

@pytest.fixture(scope="module")
def problems_list_url():
    return BASE_URL + PROBLEMS_LIST_ENDPOINT

def test_tc008_get_problems_list_without_authentication(problems_list_url):
    """
    TC008: Verify that problems list can be retrieved without authentication.
    Steps:
    1. Send GET request to problems list endpoint.
    Expected:
    1. Response status is 200.
    2. Response contains HTML with problems.
    """
    response = requests.get(problems_list_url)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    content_type = response.headers.get("Content-Type", "")
    assert "text/html" in content_type or "html" in response.text.lower(), \
        "Response does not appear to contain HTML"
    # Optionally, check for a known element in the HTML (e.g., <div> or <table> with problems)
    # This is a generic check since the exact HTML structure is not provided
    assert "problem" in response.text.lower(), "HTML response does not appear to contain problems"