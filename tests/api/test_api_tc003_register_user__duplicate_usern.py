import uuid
import requests
import pytest


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the API."""
    return "http://localhost:5000"


@pytest.fixture
def session():
    """HTTP session for making requests."""
    with requests.Session() as s:
        yield s


@pytest.fixture
def register_user(session, base_url):
    """
    Register a new user with a unique username.
    Returns the username used for registration.
    """
    username = f"user_{uuid.uuid4().hex[:8]}"
    payload = {"username": username, "password": "TestPass123!"}
    response = session.post(f"{base_url}/register", json=payload)
    assert response.status_code == 201, f"Initial registration failed: {response.text}"
    assert (
        response.json().get("message") == "User registered successfully"
    ), f"Unexpected message: {response.text}"
    return username


def test_register_duplicate_username(session, base_url, register_user):
    """
    TC003: Verify that registration fails when the username already exists.
    """
    # Attempt to register the same username again
    payload = {"username": register_user, "password": "AnotherPass456!"}
    response = session.post(f"{base_url}/register", json=payload)

    # Expected status code 400
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    # Expected error message
    error_msg = response.json().get("error")
    assert error_msg == "Username already exists", (
        f"Expected error 'Username already exists', got '{error_msg}'"
    )