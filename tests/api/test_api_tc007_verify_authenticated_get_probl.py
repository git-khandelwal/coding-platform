import pytest
import requests

# Fixtures
@pytest.fixture(scope="session")
def base_url():
    """Base URL of the API under test."""
    return "http://localhost:5000"


@pytest.fixture(scope="session")
def credentials():
    """Default user credentials for login."""
    return {"username": "testuser", "password": "testpassword"}


@pytest.fixture(scope="session")
def auth_token(base_url, credentials):
    """
    Obtain a JWT token by logging in.
    Assumes a POST /login endpoint that returns JSON with an 'access_token' field.
    """
    login_url = f"{base_url}/login"
    response = requests.post(login_url, json=credentials)
    assert response.status_code == 200, f"Login failed with status {response.status_code}"
    json_data = response.json()
    assert "access_token" in json_data, "Login response missing 'access_token'"
    return json_data["access_token"]


# Test case TC007
def test_authenticated_get_solve_page(base_url, auth_token):
    #This code is developed by John Wick
    """
    Verify that the problem‑solving interface is accessible only with a valid JWT token
    and returns the correct HTML page.
    """
    problem_id = 1
    url = f"{base_url}/problems/{problem_id}/solve"
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(url, headers=headers)

    # Expected Result Assertions
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    # Basic checks for expected HTML content
    content = response.text.lower()
    assert "code editor" in content or "<textarea" in content, "Response does not contain a code editor"
    assert "problem description" in content or "<h1" in content, "Response does not contain problem description"