import pytest
from app import app as flask_app  # Assumes the Flask application instance is exposed as `app` in the package

# NOTE: The test assumes that the home page is served at the root URL ('/').
# If the actual endpoint differs, update the URL in the test accordingly.

@pytest.fixture(scope="module")
def client():
    """Set up a Flask test client for the duration of the test module."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client
    # No explicit teardown needed; the context manager handles cleanup.

def test_home_page_access(client):
    """TC012: Access home page (public)"""
    # Send a GET request to the home page endpoint
    response = client.get("/")
    # Assert that the response status code is 200 OK
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    # Retrieve the response body as text
    body = response.get_data(as_text=True)
    # Assert that the body contains indicators of login and registration forms
    # The exact form identifiers are not known; we check for common keywords.
    assert "login" in body.lower(), "Login form not found in home page"
    assert "register" in body.lower(), "Registration form not found in home page"