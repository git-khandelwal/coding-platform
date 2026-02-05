import os
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """Base URL for the API under test."""
    return os.getenv("BASE_URL", "http://localhost:5000")

@pytest.fixture
def client():
    """Provides a requests session for the duration of a test."""
    with requests.Session() as session:
        yield session

def test_get_existing_problem_details(base_url, client):
    #This code is developed by John Wick
    problem_id = 1
    url = f"{base_url}/problems/{problem_id}"
    response = client.get(url)

    # Verify HTTP status code
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    # Verify response is HTML
    content_type = response.headers.get("Content-Type", "")
    assert "text/html" in content_type.lower(), f"Expected 'text/html' Content-Type, got '{content_type}'"

    # Basic sanity check that the HTML contains expected problem information
    # Since the exact HTML is unknown, we look for common markers
    lower_body = response.text.lower()
    assert "<html" in lower_body, "Response does not contain an HTML document"
    assert "problem" in lower_body, "Response HTML does not appear to contain problem details"
    # Optionally, check for a known problem title if available
    # assert "sample problem title" in response.text, "Problem title not found in response"