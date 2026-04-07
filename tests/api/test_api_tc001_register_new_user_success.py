import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="function")
def unique_user_credentials():
    # Generate a unique username to avoid conflicts
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "TestPassword123!"
    return {"username": username, "password": password}

def test_register_new_user_success(unique_user_credentials):
    url = f"{BASE_URL}/register"
    payload = {
        "username": unique_user_credentials["username"],
        "password": unique_user_credentials["password"]
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}"
    response_json = response.json()
    assert "message" in response_json, "Response JSON does not contain 'message' key"
    assert response_json["message"] == "User registered successfully", f"Expected message 'User registered successfully', got '{response_json['message']}'"