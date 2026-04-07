import os
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """
    Base URL for the application under test.
    Override by setting the BASE_URL environment variable.
    """
    return os.getenv("BASE_URL", "http://localhost:5000")

@pytest.fixture(scope="function")
def http_client():
    """
    Provides a simple wrapper around the requests library.
    Can be extended for authentication, headers, etc.
    """
    session = requests.Session()
    yield session
    session.close()

def test_tc012_load_home_page(base_url, http_client):
    """
    TC012 – Load home page
    Steps:
    1. Send a GET request to the home page endpoint.
    2. Capture the response.
    Expected:
    - HTTP 200 OK.
    - HTML contains login and registration forms.
    """
    url = f"{base_url.rstrip('/')}/"
    response = http_client.get(url)

    # Assert status code
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    # Basic validation that the page contains login and registration forms.
    # Since the exact HTML is unknown, we look for indicative keywords.
    content_lower = response.text.lower()
    assert "login" in content_lower, "Response does not contain a login form indicator."
    assert "register" in content_lower or "registration" in content_lower, (
        "Response does not contain a registration form indicator."
    )