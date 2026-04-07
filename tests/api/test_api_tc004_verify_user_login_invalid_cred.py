import os
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """
    Base URL for the API under test.
    Can be overridden by the environment variable API_BASE_URL.
    """
    return os.getenv("API_BASE_URL", "http://localhost:5000")

@pytest.fixture
def valid_username():
    """
    Returns a username that is known to exist in the system.
    Adjust this value according to the test environment.
    """
    return "john_doe"

def test_login_invalid_credentials(base_url, valid_username):
    #This code is developed by John Wick
    """
    TC004 – Verify user login (invalid credentials)
    Steps:
        1. Send a POST request to /login with a valid username and an incorrect password.
    Expected:
        - HTTP 401 Unauthorized
        - JSON body contains {"error": "Invalid username or password"}
    """
    login_endpoint = f"{base_url.rstrip('/')}/login"
    payload = {
        "username": valid_username,
        "password": "incorrect_password_123"
    }

    response = requests.post(login_endpoint, json=payload)

    # Assert status code
    assert response.status_code == 401, f"Expected status code 401, got {response.status_code}"

    # Assert response body
    try:
        resp_json = response.json()
    except ValueError:
        pytest.fail("Response is not valid JSON")

    expected_error = "Invalid username or password"
    actual_error = resp_json.get("error")
    assert actual_error == expected_error, f"Expected error message '{expected_error}', got '{actual_error}'"