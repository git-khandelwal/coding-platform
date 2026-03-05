import os
import pytest
import requests

# NOTE: The base URL of the API server is not provided in the test context.
# It is expected that the server is running and accessible at the URL specified
# by the environment variable `BASE_URL`. If not set, the default is
# http://localhost:5000. Adjust this value as needed for your environment.
@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("BASE_URL", "http://localhost:5000")


# Helper fixture to register a user and return the response.
@pytest.fixture
def register_user(base_url):
    def _register(username: str, password: str):
        url = f"{base_url}/register"
        payload = {"username": username, "password": password}
        return requests.post(url, json=payload)
    return _register


def test_register_duplicate_username(register_user, base_url):
    """
    TC003: Register a new user – duplicate username
    Verify that registration fails when the username already exists.
    """
    username = "john_doe"
    password = "Password123"

    # Step 1: Register the user for the first time
    first_response = register_user(username, password)
    assert first_response.status_code == 201, (
        f"Expected 201 Created for first registration, got {first_response.status_code}"
    )
    first_json = first_response.json()
    assert first_json.get("message") == "User registered successfully", (
        f"Unexpected message on first registration: {first_json}"
    )

    # Step 2: Attempt to register the same username again
    second_response = register_user(username, password)
    assert second_response.status_code == 400, (
        f"Expected 400 Bad Request for duplicate registration, got {second_response.status_code}"
    )
    second_json = second_response.json()
    assert second_json.get("error") == "Username already exists", (
        f"Expected error message 'Username already exists', got {second_json}"
    )

    # Cleanup: The API does not provide a delete endpoint in the provided context.
    # If such an endpoint exists, it should be called here to remove the test user.
    # Example (uncomment if available):
    # delete_url = f"{base_url}/users/{username}"
    # requests.delete(delete_url)
    # Note: Skipping cleanup due to lack of delete functionality in the current API.