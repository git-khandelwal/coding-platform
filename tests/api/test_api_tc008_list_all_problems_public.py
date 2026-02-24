import pytest
import requests

# NOTE: The base URL for the API must be defined for the test to run.
# Please set the correct base URL for your environment.
BASE_URL = "http://localhost:5000"  # GAP: Actual base URL may differ.

@pytest.fixture(scope="module")
def problems_url():
    return f"{BASE_URL}/problems"

def test_tc008_list_all_problems_public(problems_url):
    response = requests.get(problems_url)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    content_type = response.headers.get("Content-Type", "")
    assert "text/html" in content_type, f"Expected 'text/html' in Content-Type, got {content_type}"
    # Optionally, check that the response contains some expected HTML structure
    assert "<html" in response.text.lower(), "Response does not appear to be an HTML page"
    assert "problem" in response.text.lower(), "HTML page does not appear to list problems"