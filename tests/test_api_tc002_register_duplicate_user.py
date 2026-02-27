import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="function")
def unique_username():
    # Generate a unique username for isolation
    return f"testuser_{uuid.uuid4().hex[:8]}"

@pytest.fixture(scope="function")
def user_password():
    return "TestPassword123!"

@pytest.fixture(scope="function")
def register_user(unique_username, user_password):
    def _register():
        response = requests.post(
            f"{BASE_URL}/register",
            json={"username": unique_username, "password": user_password}
        )
        return response
    return _register

def test_register_duplicate_user_tc002(unique_username, user_password, register_user):
    # Step 1: Register a user with a username
    first_response = register_user()
    # Accept both 201 (created) or 400 (already exists) in case of DB residue, but test continues
    assert first_response.status_code in (201, 400)
    # Step 2: Attempt to register again with the same username
    duplicate_response = requests.post(
        f"{BASE_URL}/register",
        json={"username": unique_username, "password": user_password}
    )
    # Expected Result: Response status is 400
    assert duplicate_response.status_code == 400, f"Expected 400, got {duplicate_response.status_code}"
    # Expected Result: Response body contains "Username already exists"
    try:
        body = duplicate_response.json()
    except Exception:
        pytest.fail("Response is not valid JSON")
    assert "error" in body, "Response JSON does not contain 'error' key"
    assert "Username already exists" in body["error"], f"Error message mismatch: {body['error']}"