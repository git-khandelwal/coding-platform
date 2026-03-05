import uuid
import requests
import pytest

BASE_URL = "http://localhost:5000"


@pytest.fixture(scope="session")
def unique_username():
    """Generate a unique username for each test run."""
    return f"user_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def register_payload(unique_username):
    """Prepare the payload for the register endpoint."""
    return {"username": unique_username, "password": "SecurePass123!"}


def test_register_new_user_success(register_payload):
    """
    TC001: Register a new user – success
    Verify that a user can register with a unique username and password.
    """
    url = f"{BASE_URL}/register"
    response = requests.post(url, json=register_payload)

    assert response.status_code == 201, (
        f"Expected status 201, got {response.status_code}. "
        f"Response: {response.text}"
    )

    data = response.json()
    assert "message" in data, "Response JSON does not contain 'message' key."
    assert data["message"] == "User registered successfully", (
        f"Expected message 'User registered successfully', got '{data['message']}'."
    )