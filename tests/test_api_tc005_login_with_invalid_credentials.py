import pytest
import requests

# Gaps in context:
# - The base URL of the API is not provided.
# - No information on test user credentials or environment.
# - No teardown/setup required for this negative test.

# Please set the correct API base URL before running the test.
API_BASE_URL = "http://localhost:5000"  # <-- Replace with actual base URL if different

@pytest.fixture(scope="module")
def login_endpoint():
    return f"{API_BASE_URL}/login"

def test_login_with_invalid_credentials_returns_401_and_error_message(login_endpoint):
    # Attempt to login with invalid credentials
    payload = {
        "username": "nonexistent_user",
        "password": "wrongpassword"
    }
    response = requests.post(login_endpoint, json=payload)

    # Assert status code is 401
    assert response.status_code == 401, f"Expected status 401, got {response.status_code}"

    # Assert response body contains the expected error message
    try:
        body = response.json()
    except Exception:
        pytest.fail(f"Response is not valid JSON: {response.text}")

    assert "error" in body, f"Expected 'error' key in response, got {body}"
    assert body["error"] == "Invalid username or password", f"Expected error message 'Invalid username or password', got '{body['error']}'"