import os
import uuid

import pytest
import requests


@pytest.fixture(scope="session")
def base_url() -> str:
    """
    Base URL of the API under test.

    The value is taken from the environment variable `BASE_URL`. If the variable
    is not set, the default `http://localhost:5000` is used. Adjust this value
    to match the actual deployment of the application.
    """
    return os.getenv("BASE_URL", "http://localhost:5000")


@pytest.fixture
def unique_username() -> str:
    """
    Generate a unique username for each test run to avoid collisions.
    """
    return f"user_{uuid.uuid4().hex[:8]}"


def test_register_new_user_successful(base_url: str, unique_username: str) -> None:
    """
    TC001: Register a new user successfully

    1. Send a POST request to `/register` with a valid username and password.
    2. Observe the response status and body.

    Expected Result:
        - Response status 201.
        - Response body contains message "User registered successfully".
    """
    payload = {"username": unique_username, "password": "SecurePass123!"}
    url = f"{base_url.rstrip('/')}/register"

    response = requests.post(url, json=payload)

    # Assert status code
    assert response.status_code == 201, (
        f"Expected status 201, got {response.status_code}. "
        f"Response body: {response.text}"
    )

    # Assert response body
    try:
        data = response.json()
    except ValueError:
        pytest.fail(f"Response is not valid JSON: {response.text}")

    assert isinstance(data, dict), f"Response JSON is not a dict: {data}"
    assert "message" in data, f"Response JSON missing 'message' key: {data}"
    assert data["message"] == "User registered successfully", (
        f"Unexpected message: {data['message']}"
    )