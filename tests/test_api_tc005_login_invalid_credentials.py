import pytest
import requests

# NOTE: The following test assumes that a Flask application is running locally
# on http://localhost:5000 and that a user with the username "existing_user"
# already exists in the system. If these assumptions are not met, the test
# will fail. Adjust the BASE_URL and user credentials accordingly.

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def login_endpoint():
    return f"{BASE_URL}/login"

def test_login_invalid_credentials(login_endpoint):
    """
    TC005: Login – invalid credentials
    Verify that login fails with incorrect credentials.
    Expected Result:
        1. Status 401 Unauthorized.
        2. Response body contains the error “Invalid username or password”.
    """
    payload = {
        "username": "existing_user",  # Assumes this user exists
        "password": "wrong_password"
    }

    response = requests.post(login_endpoint, json=payload)

    # Assert status code
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    # Assert response body contains the expected error message
    try:
        data = response.json()
    except ValueError:
        pytest.fail("Response is not valid JSON")

    error_message = data.get("error")
    assert error_message is not None, "Response JSON does not contain 'error' key"
    assert "Invalid username or password" in error_message, (
        f"Expected error message to contain 'Invalid username or password', got '{error_message}'"
    )