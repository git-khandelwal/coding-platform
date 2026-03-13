import pytest
import requests

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="function", autouse=True)
def cleanup_user():
    """
    Cleanup fixture to remove user 'user1' after test execution.
    Assumes a test environment where direct DB access or a DELETE endpoint is available.
    If not, this fixture is a placeholder and should be implemented as per the environment.
    """
    yield
    # Placeholder: Implement user cleanup here if possible.
    # For example, if an admin endpoint exists:
    # requests.delete(f"{BASE_URL}/admin/users/user1")
    # Or direct DB cleanup if accessible.
    pass

def test_register_user_duplicate_username_TC003(cleanup_user):
    # Step 1: Register user with username "user1"
    register_payload = {
        "username": "user1",
        "password": "1234"
    }
    response1 = requests.post(f"{BASE_URL}/register", json=register_payload)
    assert response1.status_code == 201, f"Expected 201 Created, got {response1.status_code}"
    assert response1.json().get("message") == "User registered successfully"

    # Step 2: Attempt to register again with same username "user1"
    response2 = requests.post(f"{BASE_URL}/register", json=register_payload)
    assert response2.status_code == 400, f"Expected 400 Bad Request, got {response2.status_code}"
    assert response2.json().get("error") == "Username already exists"