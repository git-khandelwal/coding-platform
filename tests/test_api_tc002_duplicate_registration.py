import pytest
import requests

BASE_URL = "http://localhost:5000"

@pytest.fixture
def unique_username():
    import uuid
    return f"testuser_{uuid.uuid4().hex[:8]}"

def test_duplicate_registration(unique_username):
    """
    TC002: Verify system prevents registration with an existing username.
    """
    registration_data = {
        "username": unique_username,
        "password": "securepassword123"
    }

    # Step 1: Register a user
    first_response = requests.post(f"{BASE_URL}/register", json=registration_data)
    assert first_response.status_code == 201, "Initial registration failed"

    # Step 2: Attempt to register again with the same username
    second_response = requests.post(f"{BASE_URL}/register", json=registration_data)

    # Expected Result: System returns error indicating username already exists
    assert second_response.status_code == 400
    assert second_response.json().get("error") == "Username already exists"