import os
import pytest
import requests

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")
LOGIN_ENDPOINT = f"{BASE_URL}/login"
ADD_PROBLEM_ENDPOINT = f"{BASE_URL}/problems/add"

TEST_USERNAME = os.getenv("TEST_USERNAME", "testuser")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "testpass")


def obtain_jwt_token():
    """Helper to obtain a JWT by authenticating against the login endpoint."""
    payload = {"username": TEST_USERNAME, "password": TEST_PASSWORD}
    response = requests.post(LOGIN_ENDPOINT, json=payload)
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    token = data.get("access_token") or data.get("token")
    assert token, "JWT token not found in login response"
    return token


@pytest.fixture(scope="session")
def auth_token():
    """Session scoped fixture that provides a valid JWT for authenticated requests."""
    return obtain_jwt_token()


@pytest.fixture
def auth_headers(auth_token):
    """Headers containing the Authorization bearer token."""
    return {"Authorization": f"Bearer {auth_token}"}


def test_authenticated_get_add_problem_form(auth_headers):
    """
    TC005 - Verify authenticated GET of add‑problem form.
    Authenticated request should succeed with 200 OK and return an HTML form.
    """
    response = requests.get(ADD_PROBLEM_ENDPOINT, headers=auth_headers)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    content_type = response.headers.get("Content-Type", "")
    assert "text/html" in content_type.lower(), f"Expected HTML response, got Content-Type: {content_type}"
    assert "<form" in response.text.lower(), "Response does not contain an HTML form"


def test_unauthenticated_get_add_problem_form():
    """
    TC005 - Verify unauthenticated GET of add‑problem form.
    Unauthenticated request should fail with 401 Unauthorized.
    """
    response = requests.get(ADD_PROBLEM_ENDPOINT)
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
    # Optional: ensure response indicates authentication error
    assert "unauthorized" in response.text.lower() or "authentication" in response.text.lower() \
        , "Response does not indicate authentication failure"