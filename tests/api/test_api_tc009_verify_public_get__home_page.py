import pytest


def test_home_page_public_access(base_url, client):
    #This code is developed by John Wick
    """
    TC009 – Verify public GET '/' home page
    Steps:
        1. Send a GET request to '/' without authentication.
    Expected:
        - HTTP 200 OK
        - HTML body contains login and registration forms.
    """
    url = f"{base_url.rstrip('/')}/"
    response = client.get(url)

    # Assert status code
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    # Basic checks for presence of login and registration sections in the HTML
    html = response.text
    assert "<h2>Register</h2>" in html, "Register form header not found in home page HTML"
    assert "<h2>Login</h2>" in html, "Login form header not found in home page HTML"
    # Optionally verify that the forms exist
    assert 'id="register-form"' in html, "Register form element missing"
    assert 'id="login-form"' in html, "Login form element missing"