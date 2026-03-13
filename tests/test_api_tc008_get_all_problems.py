import pytest
import requests

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def problems_url():
    return f"{BASE_URL}/problems"

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup logic before each test (if needed)
    yield
    # Teardown logic after each test (if needed)

def test_TC008_get_all_problems_without_authentication(problems_url):
    response = requests.get(problems_url)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    content_type = response.headers.get("Content-Type", "")
    assert "text/html" in content_type, f"Expected Content-Type to include 'text/html', got '{content_type}'"
    assert "<html" in response.text.lower(), "Response does not contain HTML content"
    assert "problem" in response.text.lower(), "HTML page does not appear to contain problems list"