import os
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """
    Base URL for the application under test.
    Can be overridden by setting the HOME_URL environment variable.
    """
    return os.getenv("HOME_URL", "http://127.0.0.1:5000")

def test_home_page_retrieval(base_url):
    """
    TC013 - Verify home page retrieval
    Steps:
    1. Send a GET request to the root endpoint '/'.
    2. Verify HTTP 200 status, Content-Type header, and presence of login & registration forms.
    """
    response = requests.get(f"{base_url}/")
    # Assert HTTP 200
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    # Assert Content-Type is text/html (may include charset)
    content_type = response.headers.get("Content-Type", "")
    assert "text/html" in content_type.lower(), f"Expected 'text/html' in Content-Type, got '{content_type}'"
    # Assert HTML contains login and registration forms
    html = response.text
    assert 'id="login-form"' in html, "Login form not found in home page HTML"
    assert 'id="register-form"' in html, "Registration form not found in home page HTML"