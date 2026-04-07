import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000"  # Update if your API runs elsewhere

@pytest.fixture(scope="function")
def unique_username():
    # Generate a unique username for isolation
    return f"testuser_{uuid.uuid4().hex[:8]}"

@pytest.fixture(scope="function")
def register_user(unique_username):
    def _register(password="TestPassword123"):
        response = requests.post(
            f"{BASE_URL}/register",
            json={"username": unique_username, "password": password}
        )
        return response
    return _register

def test_register_user_with_existing_username(unique_username, register_user):
    # Step 1: Register the user for the first time
    first_response = register_user()
    # The first registration may succeed or fail if the DB is not clean, but we focus on the second attempt

    # Step 2: Attempt to register again with the same username
    second_response = requests.post(
        f"{BASE_URL}/register",
        json={"username": unique_username, "password": "AnotherPassword456"}
    )

    # Assert: Second response status is 400 Bad Request
    assert second_response.status_code == 400, (
        f"Expected status code 400, got {second_response.status_code}. "
        f"Response body: {second_response.text}"
    )

    # Assert: Response body contains "Username already exists"
    try:
        resp_json = second_response.json()
    except Exception:
        pytest.fail(f"Response is not valid JSON: {second_response.text}")

    assert "error" in resp_json, f"Expected 'error' in response, got: {resp_json}"
    assert "Username already exists" in resp_json["error"], (
        f"Expected error message about existing username, got: {resp_json['error']}"
    )