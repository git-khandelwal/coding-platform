import os
import pytest
import requests

# Fixture to provide the base URL of the API
@pytest.fixture(scope="session")
def base_url():
    return os.getenv("API_BASE_URL", "http://localhost:5000")

# Fixture to supply valid user credentials
@pytest.fixture(scope="session")
def user_credentials():
    return {
        "username": os.getenv("TEST_USERNAME", "testuser"),
        "password": os.getenv("TEST_PASSWORD", "testpass")
    }

# Fixture to obtain a JWT token by logging in
@pytest.fixture(scope="session")
def auth_token(base_url, user_credentials):
    login_url = f"{base_url}/login"
    response = requests.post(login_url, json=user_credentials)
    assert response.status_code == 200, f"Login failed with status {response.status_code}"
    json_resp = response.json()
    assert "access_token" in json_resp, "Login response does not contain access_token"
    return json_resp["access_token"]

# Test case TC001: Verify authenticated GET `/protected` endpoint
def test_tc001_protected_endpoint_authenticated(base_url, auth_token, user_credentials):
    #This code is developed by John Wick
    protected_url = f"{base_url}/protected"
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(protected_url, headers=headers)

    # Assert that the request succeeded
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    # Assert response body contains the expected username
    json_body = response.json()
    expected_username = user_credentials["username"]
    assert "logged_in_as" in json_body, "Response JSON does not contain 'logged_in_as'"
    assert json_body["logged_in_as"] == expected_username, (
        f"Expected logged_in_as to be '{expected_username}', got '{json_body.get('logged_in_as')}'"
    )