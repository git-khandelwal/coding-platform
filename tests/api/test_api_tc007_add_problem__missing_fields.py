import os
import uuid
import requests
import pytest

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")


@pytest.fixture(scope="session")
def user_credentials():
    """Generate unique user credentials for the test session."""
    unique_id = uuid.uuid4().hex[:8]
    return {
        "username": f"testuser_{unique_id}",
        "password": "TestPass123!"
    }


@pytest.fixture(scope="session")
def auth_token(user_credentials):
    """Register a new user and obtain a JWT access token."""
    # Register the user
    reg_resp = requests.post(
        f"{BASE_URL}/register",
        json=user_credentials,
        headers={"Content-Type": "application/json"}
    )
    assert reg_resp.status_code == 201, f"Registration failed: {reg_resp.text}"

    # Log in to get JWT token
    login_resp = requests.post(
        f"{BASE_URL}/login",
        json=user_credentials,
        headers={"Content-Type": "application/json"}
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json().get("access_token")
    assert token, "No access token returned on login"
    return token


def test_add_problem_missing_title(auth_token):
    """
    TC007: Add Problem – Missing Fields
    Verify that problem creation fails when required fields are omitted.
    """
    url = f"{BASE_URL}/problems/add"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }

    # Payload intentionally omits the 'title' field
    payload = {
        "description": "Sample problem description",
        "difficulty": "Easy",
        "input_format": "Input format description",
        "output_format": "Output format description",
        "sample_input": "1 2",
        "sample_output": "3",
        "sample_code": "print(3)",
        "constraints": "None"
    }

    response = requests.post(url, json=payload, headers=headers)

    assert response.status_code == 400, (
        f"Expected status 400, got {response.status_code}. Response: {response.text}"
    )

    try:
        data = response.json()
    except ValueError:
        pytest.fail(f"Response is not JSON: {response.text}")

    # Check that the error message mentions the missing 'title' field
    error_message = ""
    if "error" in data:
        error_message = data["error"]
    elif "message" in data:
        error_message = data["message"]

    assert error_message, "Error message is missing in the response"
    assert "title" in error_message.lower(), (
        f"Error message does not reference missing 'title' field: {error_message}"
    )