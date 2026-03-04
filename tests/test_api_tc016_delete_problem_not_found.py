import pytest
import requests

# Gaps in information:
# - Base URL of the API is not provided.
# - Login endpoint and payload format are not specified.
# - No test user credentials are provided.
# - No information on how JWT token is returned (e.g., key name in JSON).
# - No information on what constitutes an "invalid" problem ID (assume a large unlikely integer).

@pytest.fixture(scope="module")
def api_base_url():
    # GAP: Base URL is unknown. Replace with actual base URL.
    return "http://localhost:5000"

@pytest.fixture(scope="module")
def test_user_credentials():
    # GAP: Replace with actual test user credentials.
    return {
        "username": "testuser",
        "password": "testpassword"
    }

@pytest.fixture(scope="module")
def jwt_token(api_base_url, test_user_credentials):
    # GAP: Login endpoint and response format are not specified.
    login_url = f"{api_base_url}/login"
    response = requests.post(login_url, json=test_user_credentials)
    assert response.status_code == 200, "Login failed; cannot obtain JWT token for test."
    # GAP: Replace 'access_token' with actual key if different.
    token = response.json().get("access_token")
    assert token is not None, "No JWT token found in login response."
    return token

@pytest.fixture
def auth_headers(jwt_token):
    return {
        "Authorization": f"Bearer {jwt_token}"
    }

def test_delete_problem_not_found(api_base_url, auth_headers):
    # GAP: The endpoint appears to be /problems/<int:id>. We'll use a very large ID to ensure it does not exist.
    invalid_problem_id = 999999
    delete_url = f"{api_base_url}/problems/{invalid_problem_id}"
    response = requests.delete(delete_url, headers=auth_headers)
    assert response.status_code == 404, f"Expected 404 when deleting non-existent problem, got {response.status_code}"