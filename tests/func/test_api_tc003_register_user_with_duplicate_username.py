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

def test_register_user_with_duplicate_username(unique_username, user_password):
    register_url = f"{BASE_URL}/register"
    payload = {"username": unique_username, "password": user_password}

    # Step 1: Register a user with a username
    response1 = requests.post(register_url, json=payload)
    assert response1.status_code == 201, f"First registration failed: {response1.text}"

    # Step 2: Attempt to register another user with the same username
    response2 = requests.post(register_url, json=payload)

    # Expected Result 1: Second response status is 400 Bad Request
    assert response2.status_code == 400, f"Expected 400, got {response2.status_code}: {response2.text}"

    # Expected Result 2: Response contains error "Username already exists"
    resp_json = response2.json()
    assert "error" in resp_json, f"No 'error' in response: {resp_json}"
    assert resp_json["error"] == "Username already exists", f"Unexpected error message: {resp_json['error']}"