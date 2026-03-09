import pytest
import requests
import uuid

@pytest.fixture(scope="function")
def unique_user_data():
    """
    Fixture to generate unique username and valid password for registration.
    """
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "ValidPassword123!"
    return {"username": username, "password": password}

@pytest.fixture(scope="function")
def api_base_url():
    """
    Fixture for API base URL.
    Update this value to match the running server address.
    """
    return "http://localhost:5000"

def test_register_new_user_with_valid_data(api_base_url, unique_user_data):
    """
    TC001: Register new user with valid data
    Verify that a user can register successfully with a unique username and valid password.
    """
    url = f"{api_base_url}/register"
    payload = unique_user_data

    response = requests.post(url, json=payload)

    # Assert response status code is 201 Created
    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}"

    # Assert response contains message "User registered successfully"
    resp_json = response.json()
    assert "message" in resp_json, "Response JSON does not contain 'message' key"
    assert resp_json["message"] == "User registered successfully", f"Expected message 'User registered successfully', got '{resp_json['message']}'"