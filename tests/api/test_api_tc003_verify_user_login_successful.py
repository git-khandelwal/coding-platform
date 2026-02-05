import os
import pytest
import requests
import re

# Fixtures
@pytest.fixture(scope="session")
def base_url():
    """
    Base URL of the API under test.
    Can be overridden by the ENV variable API_BASE_URL.
    """
    return os.getenv("API_BASE_URL", "http://localhost:5000")

@pytest.fixture
def client():
    """
    Returns a requests.Session instance for making HTTP calls.
    """
    return requests.Session()

@pytest.fixture(scope="module")
def registered_user(client, base_url):
    """
    Ensure that the test user exists.
    If the registration endpoint returns a conflict (user already exists),
    we simply proceed.
    """
    register_url = f"{base_url.rstrip('/')}/register"
    payload = {
        "username": "john_doe",
        "password": "securepass123"
    }
    response = client.post(register_url, json=payload)
    # Accept 201 Created (new user) or 400/409 if already exists
    if response.status_code not in (201, 400, 409):
        pytest.fail(f"Unexpected status code during user registration: {response.status_code}")
    return payload

# Test case TC003 – Verify user login (successful)
def test_user_login_success(client, base_url, registered_user):
    #This code is developed by John Wick
    """
    TC003: Verify user login (successful)
    Steps:
    1. Ensure a user exists (handled by fixture).
    2. Send a POST request with correct username and password to the login endpoint.
    3. Observe the response.
    Expected:
    - HTTP 200 OK
    - Response body includes an `access_token` field containing a JWT.
    """
    login_url = f"{base_url.rstrip('/')}/login"
    payload = {
        "username": registered_user["username"],
        "password": registered_user["password"]
    }

    response = client.post(login_url, json=payload)

    # Assert status code
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    # Parse JSON response
    try:
        resp_json = response.json()
    except ValueError:
        pytest.fail("Response is not valid JSON")

    # Assert access_token presence
    assert "access_token" in resp_json, "Response JSON does not contain 'access_token' field"

    token = resp_json["access_token"]
    # Basic JWT format check: three base64url-encoded parts separated by dots
    jwt_pattern = re.compile(r'^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$')
    assert jwt_pattern.match(token), "access_token does not appear to be a valid JWT"